declare module 'nrrd-js' {
  interface NrrdFile {
    data: Uint8Array;
    sizes: number[];
    type: string;
    encoding: string;
    endian: string;
    space: string;
    spacings: number[];
  }

  export function parse(data: ArrayBuffer): NrrdFile;
  export function parseHeader(header: string): any;
  export function parseData(header: any, data: ArrayBuffer): Uint8Array;
}
