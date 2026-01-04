/**
 * osc 라이브러리 타입 선언
 */

declare module 'osc' {
  export interface UDPPortOptions {
    localAddress?: string;
    localPort?: number;
    remoteAddress?: string;
    remotePort?: number;
    broadcast?: boolean;
    multicastTTL?: number;
    multicastMembership?: string[];
    metadata?: boolean;
  }

  export interface OscArgument {
    type: 'i' | 'f' | 's' | 'b' | 't' | 'T' | 'F' | 'N' | 'I';
    value: number | string | boolean | Uint8Array;
  }

  export interface OscMessage {
    address: string;
    args: OscArgument[] | any[];
  }

  export class UDPPort {
    constructor(options: UDPPortOptions);

    options: UDPPortOptions;

    open(): void;
    close(): void;

    send(
      packet: OscMessage | Buffer,
      address?: string,
      port?: number
    ): void;

    on(event: 'ready', listener: () => void): this;
    on(event: 'message', listener: (oscMsg: OscMessage, timeTag?: any, info?: any) => void): this;
    on(event: 'error', listener: (error: Error) => void): this;
    on(event: 'close', listener: () => void): this;
    on(event: string, listener: (...args: any[]) => void): this;
  }
}
