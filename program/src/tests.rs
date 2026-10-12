//! Native entry-point regression tests. SVM tests supply rollback and CPI evidence.
use super::*;
use std::sync::Once;

const PUBLIC: &[u8; 64] = include_bytes!("../tests/fixtures/public.bin");
const NEW_PUBLIC: &[u8; 64] = include_bytes!("../tests/fixtures/new-public.bin");
const SOL: (&[u8], &[u8]) = (
    include_bytes!("../tests/fixtures/sol.intent"),
    include_bytes!("../tests/fixtures/sol.sig"),
);
const TOKEN: (&[u8], &[u8]) = (
    include_bytes!("../tests/fixtures/token.intent"),
    include_bytes!("../tests/fixtures/token.sig"),
);
const BURN: (&[u8], &[u8]) = (
    include_bytes!("../tests/fixtures/burn.intent"),
    include_bytes!("../tests/fixtures/burn.sig"),
);
const ROTATE: (&[u8], &[u8]) = (
    include_bytes!("../tests/fixtures/rotate.intent"),
    include_bytes!("../tests/fixtures/rotate.sig"),
);
const OLD_UNUSED: (&[u8], &[u8]) = (
    include_bytes!("../tests/fixtures/old-unused.intent"),
    include_bytes!("../tests/fixtures/old-unused.sig"),
);
const NEW_BURN: (&[u8], &[u8]) = (
    include_bytes!("../tests/fixtures/new-burn.intent"),
    include_bytes!("../tests/fixtures/new-burn.sig"),
);

struct HostRent;
impl solana_program::program_stubs::SyscallStubs for HostRent {
    fn sol_get_rent_sysvar(&self, address: *mut u8) -> u64 {
        // The native Rent::get caller provides an aligned Rent output pointer.
        unsafe { std::ptr::write(address.cast::<Rent>(), Rent::default()) };
        0
    }
}

#[derive(Clone)]
struct Account {
    key: Pubkey,
    owner: Pubkey,
    data: Vec<u8>,
    lamports: u64,
    writable: bool,
    executable: bool,
}
impl Account {
    fn new(key: Pubkey, owner: Pubkey, data: Vec<u8>, writable: bool) -> Self {
        Self {
            key,
            owner,
            data,
            lamports: 10_000_000,
            writable,
            executable: false,
        }
    }
}

struct Fixture {
    program: Pubkey,
    accounts: Vec<Account>,
}
impl Fixture {
    fn new() -> Self {
        static RENT: Once = Once::new();
        RENT.call_once(|| {
            solana_program::program_stubs::set_syscall_stubs(Box::new(HostRent));
        });
        let program = Pubkey::new_from_array([b'P'; 32]);
        let vault = [b'V'; 32];
        let (state, sb) = Pubkey::find_program_address(&[b"bunker_state", &vault], &program);
        let (treasury, tb) =
            Pubkey::find_program_address(&[b"bunker_treasury", state.as_ref()], &program);
        let (source, _) =
            Pubkey::find_program_address(&[b"bunker_token", state.as_ref()], &program);
        let mint = Pubkey::new_from_array([b'M'; 32]);
        let system = solana_program::system_program::id();
        let mut d = vec![0; HEADER + PUBLIC.len()];
        d[..8].copy_from_slice(STATE_MAGIC);
        d[8..40].copy_from_slice(&vault);
        d[40..72].fill(b'N');
        d[72..104].copy_from_slice(treasury.as_ref());
        d[136..168].copy_from_slice(mint.as_ref());
        d[168..200].copy_from_slice(source.as_ref());
        d[200] = XMSS;
        d[201..203].copy_from_slice(&1024u16.to_le_bytes());
        d[219] = sb;
        d[220] = tb;
        d[221..225].copy_from_slice(&(PUBLIC.len() as u32).to_le_bytes());
        d[225] = 1;
        d[226..230].copy_from_slice(&(PUBLIC.len() as u32).to_le_bytes());
        d[HEADER..].copy_from_slice(PUBLIC);
        Self {
            program,
            accounts: vec![
                Account::new(state, program, d, true),
                Account::new(treasury, program, vec![0; 8], true),
                Account::new(mint, spl_token::id(), vec![], false),
                Account::new(source, spl_token::id(), vec![], true),
                Account::new(Pubkey::new_from_array([b'D'; 32]), system, vec![], true),
                Account::new(spl_token::id(), system, vec![], false),
            ],
        }
    }
    fn state(&self) -> &[u8] {
        &self.accounts[0].data
    }
    fn snapshot(&self) -> Vec<(Vec<u8>, u64)> {
        self.accounts[..6]
            .iter()
            .map(|a| (a.data.clone(), a.lamports))
            .collect()
    }
    fn instruction(&mut self, staged: bool, intent: &[u8], witness: &[u8]) -> Vec<u8> {
        self.accounts.truncate(6);
        let mut data = vec![if staged {
            EXECUTE_STAGED
        } else {
            EXECUTE_INLINE
        }];
        data.extend_from_slice(&(intent.len() as u16).to_le_bytes());
        data.extend_from_slice(intent);
        if staged {
            let mut d = vec![0; STAGE_HEADER];
            d[..8].copy_from_slice(STAGE_MAGIC);
            d[8..40].copy_from_slice(self.accounts[0].key.as_ref());
            d[40..72].copy_from_slice(hashv(&[intent]).as_ref());
            d[104..112].copy_from_slice(&intent[169..177]);
            d[112..116].copy_from_slice(&intent[185..189]);
            d[116..120].copy_from_slice(&(witness.len() as u32).to_le_bytes());
            d[120..124].copy_from_slice(&(witness.len() as u32).to_le_bytes());
            d[124] = 1;
            d.extend_from_slice(witness);
            self.accounts.push(Account::new(
                Pubkey::new_from_array([b'W'; 32]),
                self.program,
                d,
                false,
            ));
        } else {
            data.extend_from_slice(witness);
        }
        data
    }
    fn call(&mut self, data: &[u8]) -> ProgramResult {
        let accounts: Vec<_> = self
            .accounts
            .iter_mut()
            .map(|a| {
                AccountInfo::new(
                    &a.key,
                    false,
                    a.writable,
                    &mut a.lamports,
                    &mut a.data,
                    &a.owner,
                    a.executable,
                    0,
                )
            })
            .collect();
        process_instruction(&self.program, &accounts, data)
    }
    fn run(&mut self, staged: bool, intent: &[u8], witness: &[u8]) -> ProgramResult {
        let data = self.instruction(staged, intent, witness);
        self.call(&data)
    }
    fn rejects(&mut self, staged: bool, intent: &[u8], witness: &[u8], error: Error) {
        let before = self.snapshot();
        assert_eq!(self.run(staged, intent, witness), Err(err(error)));
        assert_eq!(
            self.snapshot(),
            before,
            "rejection before effects changed custody state"
        );
    }
}

#[test]
fn all_canonical_actions_use_the_complete_reference_xmss_signature() {
    let fixture = Fixture::new();
    for (intent, signature) in [SOL, TOKEN, BURN, ROTATE] {
        assert_eq!(signature.len(), SIGNATURE_BYTES);
        assert_eq!(
            auth(fixture.state(), intent, signature, u32at(intent, 185)),
            Ok(())
        );
        let mut changed = intent.to_vec();
        let last = changed.len() - 1;
        changed[last] ^= 1;
        assert_eq!(
            auth(fixture.state(), &changed, signature, u32at(intent, 185)),
            Err(err(Error::InvalidSignature))
        );
    }
}

#[test]
fn inline_and_staged_sol_burn_and_rotation_have_identical_effects() {
    for (intent, signature) in [SOL, BURN, ROTATE] {
        let mut inline = Fixture::new();
        let mut staged = Fixture::new();
        let treasury_before = inline.accounts[1].lamports;
        let recipient_before = inline.accounts[4].lamports;
        assert_eq!(inline.run(false, intent, signature), Ok(()));
        assert_eq!(staged.run(true, intent, signature), Ok(()));
        assert_eq!(inline.snapshot(), staged.snapshot());
        assert_eq!(u64at(inline.state(), 211), 1);
        match intent[189] {
            1 => {
                assert_eq!(inline.accounts[1].lamports, treasury_before - 100);
                assert_eq!(inline.accounts[4].lamports, recipient_before + 100);
                assert!(used(inline.state(), 0));
            }
            3 => {
                for index in [2, 8, 9] {
                    assert!(used(inline.state(), index));
                }
            }
            4 => {
                assert_eq!(u64at(inline.state(), 203), 1);
                assert_eq!(&inline.state()[HEADER..], NEW_PUBLIC);
                assert_eq!(&inline.state()[230..358], &[0; 128]);
            }
            _ => unreachable!(),
        }
    }
}

#[test]
fn truncated_oversized_and_empty_xmss_witnesses_preserve_state() {
    for staged in [false, true] {
        for length in [0, 36, SIGNATURE_BYTES - 1, SIGNATURE_BYTES + 1] {
            let mut witness = BURN.1.to_vec();
            witness.resize(length, 0);
            Fixture::new().rejects(staged, BURN.0, &witness, Error::Witness);
        }
    }
}

#[test]
fn changed_burn_and_corrupted_signature_preserve_nonce_and_leaf() {
    for staged in [false, true] {
        let mut intent = BURN.0.to_vec();
        intent[195..199].copy_from_slice(&10u32.to_le_bytes());
        Fixture::new().rejects(staged, &intent, BURN.1, Error::InvalidSignature);
        let mut witness = BURN.1.to_vec();
        witness[2180] ^= 1;
        Fixture::new().rejects(staged, BURN.0, &witness, Error::InvalidSignature);
    }
}

#[test]
fn altered_sol_destination_amount_and_rotation_are_signature_rejections() {
    for staged in [false, true] {
        let mut fixture = Fixture::new();
        let mut intent = SOL.0.to_vec();
        intent[190..222].fill(b'E');
        fixture.accounts[4].key = Pubkey::new_from_array([b'E'; 32]);
        fixture.rejects(staged, &intent, SOL.1, Error::InvalidSignature);
        let mut intent = SOL.0.to_vec();
        intent[222..230].copy_from_slice(&101u64.to_le_bytes());
        Fixture::new().rejects(staged, &intent, SOL.1, Error::InvalidSignature);
        let mut intent = ROTATE.0.to_vec();
        intent[195] ^= 1;
        Fixture::new().rejects(staged, &intent, ROTATE.1, Error::InvalidSignature);
    }
}

#[test]
fn stale_intents_inactive_modes_and_invalid_indices_do_not_consume_leaves() {
    for staged in [false, true] {
        for (offset, byte, error) in [
            (169, 1, Error::Stale),
            (177, 1, Error::Stale),
            (168, ARRAY, Error::InactiveMode),
            (186, 4, Error::Index),
        ] {
            let mut intent = BURN.0.to_vec();
            intent[offset] = byte;
            Fixture::new().rejects(staged, &intent, BURN.1, error);
        }
    }
}

#[test]
fn accepted_burn_rejects_replay_authorizer_and_retired_leaves() {
    for staged in [false, true] {
        let mut fixture = Fixture::new();
        assert_eq!(fixture.run(staged, BURN.0, BURN.1), Ok(()));
        fixture.rejects(staged, BURN.0, BURN.1, Error::Stale);
        for index in [2u32, 8, 9] {
            let mut intent = BURN.0.to_vec();
            intent[177..185].copy_from_slice(&1u64.to_le_bytes());
            intent[185..189].copy_from_slice(&index.to_le_bytes());
            intent[191..195].copy_from_slice(&10u32.to_le_bytes());
            intent[195..199].copy_from_slice(&11u32.to_le_bytes());
            fixture.rejects(staged, &intent, BURN.1, Error::Used);
        }
    }
}

#[test]
fn rotation_accepts_fresh_authority_and_rejects_unused_old_authority() {
    for staged in [false, true] {
        let mut fixture = Fixture::new();
        let receiving_before = fixture.accounts[1..4]
            .iter()
            .map(|a| (a.key, a.lamports))
            .collect::<Vec<_>>();
        assert_eq!(fixture.run(staged, ROTATE.0, ROTATE.1), Ok(()));
        assert_eq!(
            receiving_before,
            fixture.accounts[1..4]
                .iter()
                .map(|a| (a.key, a.lamports))
                .collect::<Vec<_>>()
        );
        fixture.rejects(staged, OLD_UNUSED.0, OLD_UNUSED.1, Error::InvalidSignature);
        assert_eq!(fixture.run(staged, NEW_BURN.0, NEW_BURN.1), Ok(()));
        assert_eq!(u64at(fixture.state(), 203), 1);
        assert_eq!(u64at(fixture.state(), 211), 2);
        for index in [0, 8, 9] {
            assert!(used(fixture.state(), index));
        }
        assert!(!used(fixture.state(), 3));
    }
}

#[test]
fn malformed_inline_framing_never_reaches_authorization() {
    for data in [
        vec![],
        vec![EXECUTE_INLINE],
        vec![EXECUTE_INLINE, 0],
        vec![EXECUTE_INLINE, 189, 0],
        vec![EXECUTE_INLINE, 255, 255],
    ] {
        let mut fixture = Fixture::new();
        let before = fixture.snapshot();
        assert_eq!(fixture.call(&data), Err(err(Error::Malformed)));
        assert_eq!(fixture.snapshot(), before);
    }
    let mut fixture = Fixture::new();
    let mut data = fixture.instruction(false, BURN.0, BURN.1);
    data[3] ^= 1;
    let before = fixture.snapshot();
    assert_eq!(fixture.call(&data), Err(err(Error::Malformed)));
    assert_eq!(fixture.snapshot(), before);
}

#[test]
fn sealed_stage_is_still_bound_to_the_exact_intent_and_state() {
    for offset in [8, 40, 104, 112, 124] {
        let mut fixture = Fixture::new();
        let data = fixture.instruction(true, BURN.0, BURN.1);
        fixture.accounts[6].data[offset] ^= 1;
        let before = fixture.snapshot();
        assert_eq!(fixture.call(&data), Err(err(Error::Stage)));
        assert_eq!(fixture.snapshot(), before);
    }
}
