# Limitations and threat boundary

- Ordinary program upgrade authority and any explicit demo administrator remain trusted. Compromising those keys can change authorization/custody; they are excluded from attack fixtures.
- Relayer/funding-key compromise is simulated in isolated development fixtures. No real Ed25519 cryptanalysis or live network interception is performed.
- Mock USDC is a six-decimal standard SPL test mint with no real value. Fixture mint/freeze authority choices must appear in the deployment manifest.
- Stable receiving addresses are scoped to the same program, cluster and vault, with separate state/treasury seeds; they are not preserved across unrelated deployments.
- Stateful XMSS requires offchain signing discipline beyond the chain bitmap. Lost or uncertain journal state means abandon affected leaves or use a fresh tree; mnemonic-only restoration is not safe counter recovery.
- Host verifier agreement is not SVM execution. Simulation is not confirmed network execution. A pending RPC result is not a confirmed program rejection.
- Storage allocation, rent deposits, fees and transfer amounts are separate quantities. Additional witness staging changes operation transaction count and temporary storage.
- No production recovery, multidevice support, protected upgrade governance, audit/formal-verification claim or final UI is included.

