"""RFC 8391 XMSS-SHA2_10_256 reference signing and independent Python verification.
seed96 = SK_SEED || SK_PRF || PUB_SEED. Public = root || PUB_SEED.
This low-level sign_at MUST only be called after a durable client leaf reservation.
"""
from pathlib import Path
import ctypes, hashlib, hmac
N=32; HEIGHT=10; SIGNATURE_BYTES=2500; PUBLIC_BYTES=64
REF_COMMIT='171ccbd26f098542a67eb5d2b128281c80bd71a6'
LIB_PATH=Path(__file__).parent/'build/libxmss_reference.so'

def _lib(original=False):
    path=LIB_PATH.with_name('libxmss_original.so') if original else LIB_PATH
    lib=ctypes.CDLL(str(path))
    lib.bunker_keygen.argtypes=[ctypes.c_void_p]*3
    lib.bunker_sign_at.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_uint,ctypes.c_void_p,ctypes.c_ulonglong]
    lib.bunker_verify.argtypes=[ctypes.c_void_p]*3+[ctypes.c_ulonglong]
    return lib

def keygen(seed96):
    if len(seed96)!=96: raise ValueError('seed96 length')
    pk=ctypes.create_string_buffer(64);sk=ctypes.create_string_buffer(132)
    if _lib().bunker_keygen(pk,sk,bytes(seed96)):raise ValueError('reference keygen')
    return pk.raw,sk.raw

def sign_at(secret132,index,message,original=False):
    if len(secret132)!=132 or not 0<=index<1024:raise ValueError('key/index length')
    sig=ctypes.create_string_buffer(2500)
    if _lib(original).bunker_sign_at(sig,bytes(secret132),index,bytes(message),len(message)):raise ValueError('reference sign')
    return sig.raw

def reference_verify(public,message,signature):
    if len(public)!=64 or len(signature)!=2500 or int.from_bytes(signature[:4],'big')>=1024:return False
    return _lib().bunker_verify(bytes(public),bytes(signature),bytes(message),len(message))==0

def _hash(tag,*data):return hashlib.sha256(tag.to_bytes(32,'big')+b''.join(data)).digest()
def _prf(seed,addr,km):
    a=addr.copy();a[7]=km
    return _hash(3,seed,b''.join(x.to_bytes(4,'big') for x in a))
def _f(node,seed,addr):
    key=_prf(seed,addr,0);mask=_prf(seed,addr,1)
    return _hash(0,key,bytes(a^b for a,b in zip(node,mask)))
def _h(left,right,seed,addr):
    key=_prf(seed,addr,0);m1=_prf(seed,addr,1);m2=_prf(seed,addr,2)
    return _hash(1,key,bytes(a^b for a,b in zip(left,m1)),bytes(a^b for a,b in zip(right,m2)))

def verify(public,message,signature):
    """Return leaf index, or raise ValueError. No implicit prehash of message."""
    if len(public)!=64 or len(signature)!=2500:raise ValueError('encoding length')
    index=int.from_bytes(signature[:4],'big')
    if index>=1024:raise ValueError('leaf index out of range')
    root,seed=public[:32],public[32:]
    digest=_hash(2,signature[4:36],root,index.to_bytes(32,'big'),bytes(message))
    lengths=[n for b in digest for n in (b>>4,b&15)]
    csum=sum(15-n for n in lengths)<<4
    cb=csum.to_bytes(2,'big');lengths += [cb[0]>>4,cb[0]&15,cb[1]>>4]
    addr=[0,0,0,0,index,0,0,0];nodes=[]
    for chain,start in enumerate(lengths):
        node=signature[36+chain*32:68+chain*32];addr[5]=chain
        for step in range(start,15):
            addr[6]=step;node=_f(node,seed,addr)
        nodes.append(node)
    addr=[0,0,0,1,index,0,0,0];height=0
    while len(nodes)>1:
        addr[5]=height;new=[]
        for i in range(len(nodes)//2):
            addr[6]=i;new.append(_h(nodes[2*i],nodes[2*i+1],seed,addr))
        if len(nodes)&1:new.append(nodes[-1])
        nodes=new;height+=1
    node=nodes[0];addr=[0,0,0,2,0,0,0,0]
    for height in range(10):
        sibling=signature[2180+height*32:2212+height*32]
        addr[5]=height;addr[6]=index>>(height+1)
        node=_h(sibling,node,seed,addr) if (index>>height)&1 else _h(node,sibling,seed,addr)
    if not hmac.compare_digest(node,root):raise ValueError('XMSS root mismatch')
    return index
