import type { FC } from 'react';

export type Route = 'pitch' | 'technical';

export interface StepDef {
  id: string;
  /** only present on the technical route */
  tech?: boolean;
}

export interface SceneProps {
  /** has the step with this id been reached (on the current route)? */
  at: (id: string) => boolean;
  /** id of the step currently shown ('' before step 0) */
  cur: string;
  /** true while a state is applied without animation */
  instant: boolean;
  active: boolean;
  route: Route;
}

export interface SceneDef {
  key: string;
  exhibit: string;
  title: string;
  steps: StepDef[];
  C: FC<SceneProps>;
  /** hide the chrome (tab / route switch) on this scene */
  bare?: boolean;
  /** cheap pitch deck slide: no dossier header */
  cheap?: boolean;
}
