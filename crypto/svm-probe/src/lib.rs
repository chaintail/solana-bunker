use solana_program::{account_info::AccountInfo,entrypoint,entrypoint::ProgramResult,program_error::ProgramError,pubkey::Pubkey,hash::hashv,msg};
use bunker_xmss_verifier::{verify,Sha256};
entrypoint!(process_instruction);
struct SysHash;
impl Sha256 for SysHash {fn digest(&mut self,slices:&[&[u8]])->[u8;32]{hashv(slices).to_bytes()}}
pub fn process_instruction(_id:&Pubkey,accounts:&[AccountInfo],data:&[u8])->ProgramResult {
 // Microbench transport: [1, length_be16, repetitions_be32, slices_u8]; [2,...] loop baseline.
 if data.first()==Some(&1)||data.first()==Some(&2) {
  if data.len()!=8 {return Err(ProgramError::InvalidInstructionData);}
  let len=u16::from_be_bytes(data[1..3].try_into().unwrap()) as usize;
  let count=u32::from_be_bytes(data[3..7].try_into().unwrap());let slices=data[7];
  if !(32..=256).contains(&len)||count>2048||!(1..=3).contains(&slices){return Err(ProgramError::InvalidInstructionData);}
  let mut buffer=[0u8;256];let mut out=[0u8;32];
  for iteration in 0..count {
   buffer[..32].copy_from_slice(&out);buffer[len-1]^=(iteration&255) as u8;
   if data[0]==2 {for i in 0..32 {out[i]=out[i].wrapping_add(buffer[i]).wrapping_add(iteration as u8);}}
   else {out=match slices {1=>hashv(&[&buffer[..len]]).to_bytes(),2=>hashv(&[&buffer[..32],&buffer[32..len]]).to_bytes(),_=>hashv(&[&buffer[..16],&buffer[16..32],&buffer[32..len]]).to_bytes()};}
  }
  solana_program::program::set_return_data(&out);return Ok(());
 }
 let fixture=accounts.first().ok_or(ProgramError::NotEnoughAccountKeys)?;let bytes=fixture.try_borrow_data()?;
 if bytes.len()<64+2500 {return Err(ProgramError::InvalidInstructionData);}
 let public:&[u8;64]=bytes[..64].try_into().unwrap();let signature=&bytes[64..2564];let message=&bytes[2564..];
 match verify(public,message,signature,&mut SysHash) {Ok(index)=>{msg!("XMSS verified index {}",index);Ok(())},Err(_)=>Err(ProgramError::InvalidInstructionData)}
}
