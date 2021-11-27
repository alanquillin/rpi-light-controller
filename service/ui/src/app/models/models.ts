// since these will often be python API driven snake_case names
/* eslint-disable @typescript-eslint/naming-convention */
// this check reports that some of these types shadow their own definitions
/* eslint-disable no-shadow */

export class Zone {
  id: number | undefined;
  description: string | undefined;
  program: string | undefined;
  state: string | undefined;
  pin_num: number | undefined;
  on: string | undefined;
  off: string | undefined;
}