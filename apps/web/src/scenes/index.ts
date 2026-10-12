import type { Route, SceneDef } from '../types';
import { C0 } from './cheap/C0Opener';
import { C1 } from './cheap/C1Warning';
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

/** pitch route: the cheap deck (slides still being converted use the dossier scene) */
export const CHEAP: SceneDef[] = [C0, C1, S2, S3, S4, S5, S6, S7, S8, S9];

export const DECKS: Record<Route, SceneDef[]> = { pitch: CHEAP, technical: DOSSIER };
