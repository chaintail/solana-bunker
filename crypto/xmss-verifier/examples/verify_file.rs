use bunker_xmss_verifier::{verify,Sha256};
#[link(name="crypto")]
extern "C" {fn SHA256(data:*const u8,len:usize,out:*mut u8)->*mut u8;}
struct NativeHash {calls:u64,bytes:u64}
impl Sha256 for NativeHash {fn digest(&mut self,slices:&[&[u8]])->[u8;32] {
 let bytes:Vec<u8>=slices.iter().flat_map(|x|x.iter().copied()).collect();self.calls+=1;self.bytes+=bytes.len() as u64;
 let mut out=[0;32];unsafe{SHA256(bytes.as_ptr(),bytes.len(),out.as_mut_ptr());}out
}}
fn main(){let args:Vec<String>=std::env::args().collect();let pk=std::fs::read(&args[1]).unwrap();let msg=std::fs::read(&args[2]).unwrap();let sig=std::fs::read(&args[3]).unwrap();let mut h=NativeHash{calls:0,bytes:0};let r=verify(pk.as_slice().try_into().unwrap(),&msg,&sig,&mut h);println!("result={r:?} sha256_calls={} sha256_input_bytes={}",h.calls,h.bytes);if r.is_err(){std::process::exit(1)}}
