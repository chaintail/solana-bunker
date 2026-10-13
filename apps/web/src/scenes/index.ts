import type { Route, SceneDef } from '../types';
import { C0 } from './cheap/C0Opener';
import { C1 } from './cheap/C1Warning';
import { C2 } from './cheap/C2Papers';
import { C3 } from './cheap/C3Bunker';
import { C4 } from './cheap/C4V1';
import { C6 } from './cheap/C6Sig';
import { C7 } from './cheap/C7Rekey';
import { C8 } from './cheap/C8Devnet';
import { C9 } from './cheap/C9Close';
import { S0 } from './S0Opener';
import { S1 } from './S1Warning';
import { S2 } from './S2Conspiracy';
import { S3 } from './S3Bunker';
import { S4 } from './S4V1';
import { S5 } from './S5V2';
import { S6 } from './S6Signature';
import { S7 } from './S7Rekey';
import { S8 } from './S8Devnet';
import { S9 } from './S9Close';

/** technical route: the dossier deck, intact, with its technical-only steps */
export const DOSSIER: SceneDef[] = [S0, S1, S2, S3, S4, S5, S6, S7, S8, S9];

/** pitch route (default): the deliberately cheap deck */
export const CHEAP: SceneDef[] = [C0, C1, C2, C3, C4, C6, C7, C8, C9];

/** scene index in one route -> matching scene in the other (pitch slide 5 covers dossier beats 4 and 5) */
export const TWINS: Record<Route, number[]> = { pitch: [0, 1, 2, 3, 4, 6, 7, 8, 9], technical: [0, 1, 2, 3, 4, 4, 5, 6, 7, 8] };

export const DECKS: Record<Route, SceneDef[]> = { pitch: CHEAP, technical: DOSSIER };
