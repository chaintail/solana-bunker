//! Solana Bunker research program. Trusted bootstrap/demo admin is explicitly
//! retained; normal execution has no admin withdrawal bypass.
use solana_program::{account_info::{next_account_info, AccountInfo}, entrypoint::ProgramResult,
    hash::hashv, msg, program::{invoke, invoke_signed}, program_error::ProgramError,
    program_pack::Pack, pubkey::Pubkey, rent::Rent, system_instruction, sysvar::Sysvar};
use spl_token::state::{Account as TokenAccount, AccountState, Mint};
use bunker_xmss_verifier::{verify, Sha256};
#[cfg(not(feature="no-entrypoint"))]
solana_program::entrypoint!(process_instruction);

pub const HEADER: usize = 358;
pub const STAGE_HEADER: usize = 125;
const STATE_MAGIC: &[u8;8] = b"BUNKST01";
const STAGE_MAGIC: &[u8;8] = b"BUNKW001";
const ARRAY: u8=1; const MERKLE: u8=2; const XMSS: u8=3;
#[derive(Clone,Copy)]
#[repr(u32)]
pub enum Error { Malformed=1, Accounts=2, Privilege=3, Initialized=4, Incomplete=5,
    Domain=6, InactiveMode=7, Stale=8, Used=9, Index=10, Witness=11, InvalidSignature=12,
    Burn=13, Rotation=14, Token=15, Amount=16, Overflow=17, Rent=18, Stage=19 }
fn err(e:Error)->ProgramError { ProgramError::Custom(e as u32) }
fn check(b:bool,e:Error)->ProgramResult { if b {Ok(())}else{Err(err(e))} }
fn u16at(b:&[u8],o:usize)->u16 {u16::from_le_bytes(b[o..o+2].try_into().unwrap())}
fn u32at(b:&[u8],o:usize)->u32 {u32::from_le_bytes(b[o..o+4].try_into().unwrap())}
fn u64at(b:&[u8],o:usize)->u64 {u64::from_le_bytes(b[o..o+8].try_into().unwrap())}
fn keyat(b:&[u8],o:usize)->Pubkey {Pubkey::new_from_array(b[o..o+32].try_into().unwrap())}
fn used(b:&[u8],i:u32)->bool {b[230+i as usize/8]&(1<<(i%8))!=0}
fn consume(b:&mut[u8],i:u32){b[230+i as usize/8]|=1<<(i%8);}
fn authority_len(mode:u8,count:u16)->Result<usize,ProgramError>{
    check(count>0 && count<=1024 && count.is_power_of_two(),Error::Index)?;
    match mode {ARRAY=>Ok(count as usize*32),MERKLE=>Ok(32),XMSS=>{check(count==1024,Error::Index)?;Ok(64)},_=>Err(err(Error::InactiveMode))}
}
fn signer(a:&AccountInfo)->ProgramResult {check(a.is_signer,Error::Privilege)}
fn writable(a:&AccountInfo)->ProgramResult {check(a.is_writable,Error::Privilege)}
fn system(a:&AccountInfo)->ProgramResult {check(*a.key==solana_program::system_program::id(),Error::Accounts)}
fn create<'a>(payer:&AccountInfo<'a>,a:&AccountInfo<'a>,sys:&AccountInfo<'a>,owner:&Pubkey,len:usize,seeds:Option<&[&[u8]]>)->ProgramResult{
    signer(payer)?;writable(payer)?;writable(a)?;system(sys)?;
    check(a.data_is_empty() && *a.owner==solana_program::system_program::id() && !a.executable,Error::Initialized)?;
    if seeds.is_none(){signer(a)?;}
    let rent=Rent::get()?.minimum_balance(len);
    let infos=[payer.clone(),a.clone(),sys.clone()];
    let call=|ix:&solana_program::instruction::Instruction|->ProgramResult{
        match seeds {Some(s)=>invoke_signed(ix,&infos,&[s]),None=>invoke(ix,&infos)}
    };
    if a.lamports()==0 {
        call(&system_instruction::create_account(payer.key,a.key,rent,len as u64,owner))
    } else {
        // A public PDA can receive SOL before bootstrap. Preserve that deposit;
        // canonical PDA signer privileges permit allocation/assignment, while
        // the system owner + empty-data check forbids initialized re-use.
        let topup=rent.saturating_sub(a.lamports());
        if topup>0 {invoke(&system_instruction::transfer(payer.key,a.key,topup),&infos)?;}
        call(&system_instruction::allocate(a.key,len as u64))?;
        call(&system_instruction::assign(a.key,owner))
    }
}
fn valid_state(program:&Pubkey,s:&AccountInfo)->ProgramResult{
    check(s.owner==program,Error::Accounts)?;
    let d=s.try_borrow_data()?;
    check(d.len()>=HEADER && &d[..8]==STATE_MAGIC,Error::Malformed)?;
    let vault=keyat(&d,8);let (expected,bump)=Pubkey::find_program_address(&[b"bunker_state",vault.as_ref()],program);
    check(expected==*s.key && bump==d[219],Error::Accounts)
}
fn init(program:&Pubkey,a:&[AccountInfo],p:&[u8])->ProgramResult {
    check(p.len()==67,Error::Malformed)?;
    let mode=p[64];let count=u16at(p,65);let alen=authority_len(mode,count)?;
    let mut it=a.iter();let payer=next_account_info(&mut it)?;let state=next_account_info(&mut it)?;
    let treasury=next_account_info(&mut it)?;let source=next_account_info(&mut it)?;let mint=next_account_info(&mut it)?;
    let sys=next_account_info(&mut it)?;let token=next_account_info(&mut it)?;
    check(*token.key==spl_token::id() && token.executable && mint.owner==token.key,Error::Token)?;
    let md=Mint::unpack(&mint.try_borrow_data()?)?;
    check(md.decimals==6 && md.is_initialized && md.freeze_authority.is_none(),Error::Token)?;
    let (sk,sb)=Pubkey::find_program_address(&[b"bunker_state",&p[..32]],program);
    let (tk,tb)=Pubkey::find_program_address(&[b"bunker_treasury",state.key.as_ref()],program);
    let (token_key,cb)=Pubkey::find_program_address(&[b"bunker_token",state.key.as_ref()],program);
    check(*state.key==sk && *treasury.key==tk && *source.key==token_key,Error::Accounts)?;
    create(payer,state,sys,program,(HEADER+alen).min(10_000),Some(&[b"bunker_state",&p[..32],&[sb]]))?;
    create(payer,treasury,sys,program,8,Some(&[b"bunker_treasury",state.key.as_ref(),&[tb]]))?;
    create(payer,source,sys,token.key,TokenAccount::LEN,Some(&[b"bunker_token",state.key.as_ref(),&[cb]]))?;
    invoke(&spl_token::instruction::initialize_account3(token.key,source.key,mint.key,treasury.key)?,&[source.clone(),mint.clone(),token.clone()])?;
    let mut d=state.try_borrow_mut_data()?;d[..8].copy_from_slice(STATE_MAGIC);
    d[8..40].copy_from_slice(&p[..32]);d[40..72].copy_from_slice(&p[32..64]);d[72..104].copy_from_slice(treasury.key.as_ref());
    d[104..136].copy_from_slice(payer.key.as_ref());d[136..168].copy_from_slice(mint.key.as_ref());d[168..200].copy_from_slice(source.key.as_ref());
    d[200]=mode;d[201..203].copy_from_slice(&count.to_le_bytes());d[219]=sb;d[220]=tb;d[221..225].copy_from_slice(&(alen as u32).to_le_bytes());
    msg!("vault_initialized_pending_authority");Ok(())
}
fn write_authority(program:&Pubkey,a:&[AccountInfo],p:&[u8])->ProgramResult{
    check(p.len()>4 && p.len()<=904,Error::Malformed)?;
    let mut it=a.iter();let admin=next_account_info(&mut it)?;let state=next_account_info(&mut it)?;let sys=next_account_info(&mut it)?;
    signer(admin)?;writable(state)?;valid_state(program,state)?;
    let (len,written,owner,ready)={let d=state.try_borrow_data()?;(u32at(&d,221)as usize,u32at(&d,226)as usize,keyat(&d,104),d[225])};
    check(*admin.key==owner && ready==0 && u32at(p,0)as usize==written,Error::Privilege)?;
    let end=written.checked_add(p.len()-4).ok_or(err(Error::Overflow))?;check(end<=len,Error::Malformed)?;
    let needed=HEADER+end;
    if needed>state.data_len(){let extra=Rent::get()?.minimum_balance(needed).saturating_sub(state.lamports());
        if extra>0 {invoke(&system_instruction::transfer(admin.key,state.key,extra),&[admin.clone(),state.clone(),sys.clone()])?;}
        state.realloc(needed,true)?;
    }
    let mut d=state.try_borrow_mut_data()?;d[HEADER+written..HEADER+end].copy_from_slice(&p[4..]);d[226..230].copy_from_slice(&(end as u32).to_le_bytes());
    if end==len {d[225]=1;msg!("authority_finalized");}Ok(())
}
struct RuntimeHash;
impl Sha256 for RuntimeHash {fn digest(&mut self,slices:&[&[u8]])->[u8;32]{hashv(slices).to_bytes()}}
fn auth(d:&[u8],intent:&[u8],w:&[u8],index:u32)->ProgramResult{
    let count=u16at(d,201)as u32;check(index<count,Error::Index)?;check(!used(d,index),Error::Used)?;
    let authority=&d[HEADER..HEADER+u32at(d,221)as usize];
    match d[200] {
      ARRAY=>{check(w.len()==36 && u32at(w,0)==index,Error::Witness)?;check(hashv(&[&w[4..]]).as_ref()==&authority[index as usize*32..index as usize*32+32],Error::InvalidSignature)},
      MERKLE=>{let depth=count.trailing_zeros()as usize;check(w.len()==36+depth*32 && u32at(w,0)==index,Error::Witness)?;
        let secret_hash=hashv(&[&w[4..36]]);let mut node=hashv(&[b"BUNKER-LEAF-V1\0",&w[..4],secret_hash.as_ref()]).to_bytes();
        for level in 0..depth {let sibling=&w[36+32*level..68+32*level];node=if index&(1<<level)==0 {hashv(&[b"BUNKER-NODE-V1\0",&node,sibling]).to_bytes()}else{hashv(&[b"BUNKER-NODE-V1\0",sibling,&node]).to_bytes()};}
        check(node.as_ref()==authority,Error::InvalidSignature)},
      XMSS=>{check(w.len()==2500,Error::Witness)?;let public:&[u8;64]=authority.try_into().map_err(|_|err(Error::Malformed))?;
        let actual=verify(public,intent,w,&mut RuntimeHash).map_err(|_|err(Error::InvalidSignature))?;check(actual==index,Error::Witness)},
      _=>Err(err(Error::InactiveMode))
    }
}
fn execute(program:&Pubkey,a:&[AccountInfo],p:&[u8],staged:bool)->ProgramResult{
    check(p.len()>=2,Error::Malformed)?;let ilen=u16at(p,0)as usize;check(ilen>=190 && p.len()>=2+ilen,Error::Malformed)?;
    let intent=&p[2..2+ilen];check(&intent[..8]==b"BUNKER\0\x01",Error::Malformed)?;
    let mut it=a.iter();let state=next_account_info(&mut it)?;let treasury=next_account_info(&mut it)?;let mint=next_account_info(&mut it)?;
    let source=next_account_info(&mut it)?;let destination=next_account_info(&mut it)?;let token=next_account_info(&mut it)?;
    writable(state)?;writable(treasury)?;valid_state(program,state)?;check(treasury.owner==program,Error::Accounts)?;
    let stage_data;let witness=if staged {check(p.len()==2+ilen,Error::Malformed)?;let stage=next_account_info(&mut it)?;
        check(stage.owner==program && stage.key!=state.key && stage.key!=treasury.key,Error::Stage)?;
        stage_data=stage.try_borrow_data()?;let d=&stage_data;
        check(d.len()>=STAGE_HEADER && &d[..8]==STAGE_MAGIC && d[124]==1,Error::Stage)?;
        check(keyat(d,8)==*state.key && &d[40..72]==hashv(&[intent]).as_ref() && u64at(d,104)==u64at(intent,169) && u32at(d,112)==u32at(intent,185),Error::Stage)?;
        check(d.len()==STAGE_HEADER+u32at(d,116)as usize,Error::Stage)?;&d[STAGE_HEADER..]
      }else{&p[2+ilen..]};
    let mut d=state.try_borrow_mut_data()?;
    check(d[225]==1 && d.len()>=HEADER+u32at(&d,221)as usize,Error::Incomplete)?;
    check(keyat(intent,8)==*program && keyat(intent,40)==keyat(&d,40) && keyat(intent,72)==keyat(&d,8) && keyat(intent,104)==*state.key && keyat(intent,136)==*treasury.key && keyat(&d,72)==*treasury.key,Error::Domain)?;
    let (expected,tb)=Pubkey::find_program_address(&[b"bunker_treasury",state.key.as_ref()],program);check(expected==*treasury.key && tb==d[220],Error::Accounts)?;
    check(intent[168]==d[200],Error::InactiveMode)?;check(u64at(intent,169)==u64at(&d,203) && u64at(intent,177)==u64at(&d,211),Error::Stale)?;
    let index=u32at(intent,185);let action=intent[189];let fields=&intent[190..];
    let nonce=u64at(&d,211).checked_add(1).ok_or(err(Error::Overflow))?;
    match action {
      1=>{check(fields.len()==40,Error::Malformed)?;writable(destination)?;check(keyat(fields,0)==*destination.key && destination.key!=state.key && destination.key!=treasury.key && *destination.key!=keyat(&d,168),Error::Accounts)?;
        check(u64at(fields,32)>0,Error::Amount)?;destination.lamports().checked_add(u64at(fields,32)).ok_or(err(Error::Overflow))?;},
      2=>{check(fields.len()==137,Error::Malformed)?;writable(source)?;writable(destination)?;
        check(keyat(fields,0)==spl_token::id() && *token.key==spl_token::id() && token.executable && mint.owner==token.key && source.owner==token.key && destination.owner==token.key,Error::Token)?;
        check(keyat(fields,32)==*mint.key && keyat(&d,136)==*mint.key && keyat(fields,64)==*source.key && keyat(&d,168)==*source.key && keyat(fields,96)==*destination.key && destination.key!=source.key && fields[136]==6 && u64at(fields,128)>0,Error::Token)?;
        let m=Mint::unpack(&mint.try_borrow_data()?)?;let src=TokenAccount::unpack(&source.try_borrow_data()?)?;let dst=TokenAccount::unpack(&destination.try_borrow_data()?)?;
        check(m.decimals==6 && src.mint==*mint.key && dst.mint==*mint.key && src.owner==*treasury.key && src.delegate.is_none() && src.close_authority.is_none() && src.state==AccountState::Initialized && dst.state==AccountState::Initialized,Error::Token)?;},
      3=>{check(!fields.is_empty() && fields[0]>0 && fields[0]<=32 && fields.len()==1+4*fields[0]as usize,Error::Burn)?;
        let mut prev=None;for chunk in fields[1..].chunks_exact(4){let target=u32at(chunk,0);check(target<u16at(&d,201)as u32 && target!=index && !used(&d,target) && prev.map(|v|v<target).unwrap_or(true),Error::Burn)?;prev=Some(target);}},
      4=>{check(fields.len()==69 && d[200]==XMSS && fields[0]==XMSS && u32at(fields,1)==1 && fields[5..]!=d[HEADER..HEADER+64],Error::Rotation)?;u64at(&d,203).checked_add(1).ok_or(err(Error::Overflow))?;},
      _=>return Err(err(Error::Malformed))
    }
    auth(&d,intent,witness,index)?;
    consume(&mut d,index);d[211..219].copy_from_slice(&nonce.to_le_bytes());
    match action {
      1=>{let amount=u64at(fields,32);let remaining=treasury.lamports().checked_sub(amount).ok_or(err(Error::Amount))?;
        check(remaining>=Rent::get()?.minimum_balance(treasury.data_len()),Error::Rent)?;
        **treasury.try_borrow_mut_lamports()?=remaining;let new=destination.lamports().checked_add(amount).ok_or(err(Error::Overflow))?;**destination.try_borrow_mut_lamports()?=new;msg!("withdrawal_sol");},
      2=>{let bump=[d[220]];drop(d);
        invoke_signed(&spl_token::instruction::transfer_checked(token.key,source.key,mint.key,destination.key,treasury.key,&[],u64at(fields,128),6)?,&[source.clone(),mint.clone(),destination.clone(),treasury.clone(),token.clone()],&[&[b"bunker_treasury",state.key.as_ref(),&bump]])?;msg!("withdrawal_mock_usdc");},
      3=>{for chunk in fields[1..].chunks_exact(4){consume(&mut d,u32at(chunk,0));}msg!("leaves_burned");},
      4=>{let epoch=u64at(&d,203)+1;d[203..211].copy_from_slice(&epoch.to_le_bytes());d[230..358].fill(0);d[HEADER..HEADER+64].copy_from_slice(&fields[5..]);msg!("authority_rotated");},
      _=>unreachable!()
    }Ok(())
}
fn stage_init(program:&Pubkey,a:&[AccountInfo],p:&[u8])->ProgramResult{
    check(p.len()>=2,Error::Malformed)?;let n=u16at(p,0)as usize;check(n>=190 && p.len()==2+n+4,Error::Malformed)?;let intent=&p[2..2+n];
    check(&intent[..8]==b"BUNKER\0\x01" && keyat(intent,8)==*program && intent[168]==XMSS,Error::Domain)?;
    let len=u32at(p,2+n)as usize;check(len==2500,Error::Stage)?;
    let mut it=a.iter();let payer=next_account_info(&mut it)?;let stage=next_account_info(&mut it)?;let state=next_account_info(&mut it)?;let sys=next_account_info(&mut it)?;
    valid_state(program,state)?;check(*state.key==keyat(intent,104),Error::Domain)?;
    create(payer,stage,sys,program,STAGE_HEADER+len,None)?;
    let mut d=stage.try_borrow_mut_data()?;d[..8].copy_from_slice(STAGE_MAGIC);d[8..40].copy_from_slice(state.key.as_ref());d[40..72].copy_from_slice(hashv(&[intent]).as_ref());d[72..104].copy_from_slice(payer.key.as_ref());
    d[104..112].copy_from_slice(&intent[169..177]);d[112..116].copy_from_slice(&intent[185..189]);d[116..120].copy_from_slice(&(len as u32).to_le_bytes());Ok(())
}
fn stage_write(program:&Pubkey,a:&[AccountInfo],p:&[u8])->ProgramResult{
    check(p.len()>4 && p.len()<=904,Error::Malformed)?;let mut it=a.iter();let creator=next_account_info(&mut it)?;let stage=next_account_info(&mut it)?;signer(creator)?;writable(stage)?;
    check(stage.owner==program,Error::Stage)?;let mut d=stage.try_borrow_mut_data()?;check(d.len()>=STAGE_HEADER && &d[..8]==STAGE_MAGIC && keyat(&d,72)==*creator.key && d[124]==0,Error::Stage)?;
    let written=u32at(&d,120)as usize;let total=u32at(&d,116)as usize;check(u32at(p,0)as usize==written && written+p.len()-4<=total && d.len()==STAGE_HEADER+total,Error::Stage)?;
    let end=written+p.len()-4;d[STAGE_HEADER+written..STAGE_HEADER+end].copy_from_slice(&p[4..]);d[120..124].copy_from_slice(&(end as u32).to_le_bytes());if end==total{d[124]=1;}Ok(())
}
fn demo_mode(program:&Pubkey,a:&[AccountInfo],p:&[u8])->ProgramResult{
    check(p.len()==3,Error::Malformed)?;let mode=p[0];let count=u16at(p,1);let alen=authority_len(mode,count)?;
    let mut it=a.iter();let admin=next_account_info(&mut it)?;let state=next_account_info(&mut it)?;let sys=next_account_info(&mut it)?;signer(admin)?;writable(state)?;valid_state(program,state)?;
    let (epoch,nonce)={let d=state.try_borrow_data()?;check(*admin.key==keyat(&d,104),Error::Privilege)?;(u64at(&d,203).checked_add(1).ok_or(err(Error::Overflow))?,u64at(&d,211).checked_add(1).ok_or(err(Error::Overflow))?)};
    let target=(HEADER+alen).min(10_000);if target>state.data_len(){let extra=Rent::get()?.minimum_balance(target).saturating_sub(state.lamports());if extra>0{invoke(&system_instruction::transfer(admin.key,state.key,extra),&[admin.clone(),state.clone(),sys.clone()])?;}}
    state.realloc(target,true)?;let mut d=state.try_borrow_mut_data()?;d[200]=mode;d[201..203].copy_from_slice(&count.to_le_bytes());d[203..211].copy_from_slice(&epoch.to_le_bytes());d[211..219].copy_from_slice(&nonce.to_le_bytes());d[221..225].copy_from_slice(&(alen as u32).to_le_bytes());d[225]=0;d[226..230].fill(0);d[230..].fill(0);msg!("trusted_demo_admin_transition");Ok(())
}
pub fn process_instruction(program:&Pubkey,accounts:&[AccountInfo],data:&[u8])->ProgramResult{
    check(!data.is_empty(),Error::Malformed)?;
    match data[0]{0=>init(program,accounts,&data[1..]),1=>write_authority(program,accounts,&data[1..]),2=>execute(program,accounts,&data[1..],false),3=>execute(program,accounts,&data[1..],true),4=>stage_init(program,accounts,&data[1..]),5=>stage_write(program,accounts,&data[1..]),6=>demo_mode(program,accounts,&data[1..]),_=>Err(err(Error::Malformed))}
}
