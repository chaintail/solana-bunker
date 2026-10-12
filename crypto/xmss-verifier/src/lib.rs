//! Exact RFC 8391 XMSS-SHA2_10_256 verifier. Hash backend supplied by caller.
#![no_std]
extern crate alloc;
use alloc::vec;
pub const SIGNATURE_BYTES: usize = 2500;
pub const PUBLIC_BYTES: usize = 64;
pub trait Sha256 { fn digest(&mut self, slices: &[&[u8]]) -> [u8; 32]; }
#[derive(Debug,Clone,Copy,PartialEq,Eq)]
pub enum VerifyError { EncodingLength, IndexOutOfRange, RootMismatch }
fn tag(n:u32)->[u8;32] { let mut t=[0;32];t[28..].copy_from_slice(&n.to_be_bytes());t }
#[inline(never)]
fn prf<H:Sha256>(h:&mut H,seed:&[u8],addr:&[u32;8],km:u32)->[u8;32] {
 let mut a=[0;32];for i in 0..8 {a[i*4..i*4+4].copy_from_slice(&(if i==7 {km}else{addr[i]}).to_be_bytes());}
 h.digest(&[&tag(3),seed,&a])
}
#[inline(never)]
fn f<H:Sha256>(h:&mut H,node:&[u8;32],seed:&[u8],addr:&[u32;8])->[u8;32] {
 let key=prf(h,seed,addr,0);let mask=prf(h,seed,addr,1);let mut x=[0;32];
 for i in 0..32 {x[i]=node[i]^mask[i];}h.digest(&[&tag(0),&key,&x])
}
#[inline(never)]
fn rh<H:Sha256>(h:&mut H,left:&[u8;32],right:&[u8;32],seed:&[u8],addr:&[u32;8])->[u8;32] {
 let key=prf(h,seed,addr,0);let m1=prf(h,seed,addr,1);let m2=prf(h,seed,addr,2);
 let mut x=[0;64];for i in 0..32 {x[i]=left[i]^m1[i];x[32+i]=right[i]^m2[i];}
 h.digest(&[&tag(1),&key,&x])
}
/// Borrows raw 2500-byte signature; public is root || public seed, with no OID.
/// Returns authenticated signing index; caller checks epoch, intent and replay state.
#[inline(never)]
pub fn verify<H:Sha256>(public:&[u8;64],message:&[u8],signature:&[u8],h:&mut H)->Result<u32,VerifyError> {
 if signature.len()!=2500 {return Err(VerifyError::EncodingLength);}
 let index=u32::from_be_bytes(signature[..4].try_into().unwrap());
 if index>=1024 {return Err(VerifyError::IndexOutOfRange);}
 let root=&public[..32];let seed=&public[32..];let mut ib=[0;32];ib[28..].copy_from_slice(&index.to_be_bytes());
 let digest=h.digest(&[&tag(2),&signature[4..36],root,&ib,message]);
 let mut lengths=[0u8;67];let mut csum=0u16;
 for i in 0..32 {lengths[2*i]=digest[i]>>4;lengths[2*i+1]=digest[i]&15;}
 for x in &lengths[..64] {csum+=15-*x as u16;}csum<<=4;
 let cb=csum.to_be_bytes();lengths[64]=cb[0]>>4;lengths[65]=cb[0]&15;lengths[66]=cb[1]>>4;
 // Heap workspace is exactly 2144 bytes; no large SBF stack frame.
 let mut nodes=vec![[0u8;32];67];let mut addr=[0,0,0,0,index,0,0,0];
 for chain in 0..67 {let mut node=[0;32];node.copy_from_slice(&signature[36+chain*32..68+chain*32]);addr[5]=chain as u32;
  for step in lengths[chain]..15 {addr[6]=step as u32;node=f(h,&node,seed,&addr);}nodes[chain]=node;
 }
 addr=[0,0,0,1,index,0,0,0];let mut count=67;let mut height=0;
 while count>1 {addr[5]=height;
  for i in 0..count/2 {addr[6]=i as u32;nodes[i]=rh(h,&nodes[2*i],&nodes[2*i+1],seed,&addr);}
  if count%2==1 {nodes[count/2]=nodes[count-1];}count=(count+1)/2;height+=1;
 }
 let mut node=nodes[0];addr=[0,0,0,2,0,0,0,0];
 for height in 0..10 {let mut sibling=[0;32];sibling.copy_from_slice(&signature[2180+height*32..2212+height*32]);
  addr[5]=height as u32;addr[6]=index>>(height+1);
  node=if(index>>height)&1==1 {rh(h,&sibling,&node,seed,&addr)}else{rh(h,&node,&sibling,seed,&addr)};
 }
 let mut difference=0u8;for i in 0..32 {difference|=node[i]^root[i];}
 if difference!=0 {return Err(VerifyError::RootMismatch);}Ok(index)
}
