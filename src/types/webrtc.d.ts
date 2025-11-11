/**
 * WebRTC Type Declarations
 *
 * These types are for compatibility across browser and Node.js environments.
 * In browser: uses native WebRTC APIs
 * In Node.js: use wrtc package (npm install wrtc)
 */

declare global {
  interface RTCIceServer {
    urls: string | string[];
    username?: string;
    credential?: string;
  }

  interface RTCConfiguration {
    iceServers?: RTCIceServer[];
    iceTransportPolicy?: 'all' | 'relay';
    bundlePolicy?: 'balanced' | 'max-compat' | 'max-bundle';
    rtcpMuxPolicy?: 'negotiate' | 'require';
  }

  interface RTCSessionDescriptionInit {
    type: RTCSdpType;
    sdp?: string;
  }

  type RTCSdpType = 'offer' | 'pranswer' | 'answer' | 'rollback';

  interface RTCIceCandidateInit {
    candidate?: string;
    sdpMLineIndex?: number | null;
    sdpMid?: string | null;
    usernameFragment?: string | null;
  }

  class RTCPeerConnection {
    constructor(configuration?: RTCConfiguration);

    localDescription: RTCSessionDescriptionInit | null;
    remoteDescription: RTCSessionDescriptionInit | null;
    signalingState: RTCSignalingState;
    connectionState: RTCPeerConnectionState;

    createOffer(options?: RTCOfferOptions): Promise<RTCSessionDescriptionInit>;
    createAnswer(options?: RTCAnswerOptions): Promise<RTCSessionDescriptionInit>;
    setLocalDescription(description: RTCSessionDescriptionInit): Promise<void>;
    setRemoteDescription(description: RTCSessionDescriptionInit): Promise<void>;
    addIceCandidate(candidate: RTCIceCandidateInit): Promise<void>;

    createDataChannel(label: string, dataChannelDict?: RTCDataChannelInit): RTCDataChannel;

    close(): void;

    onicecandidate: ((event: RTCPeerConnectionIceEvent) => void) | null;
    onconnectionstatechange: (() => void) | null;
    ondatachannel: ((event: RTCDataChannelEvent) => void) | null;
  }

  class RTCSessionDescription {
    constructor(descriptionInitDict: RTCSessionDescriptionInit);
    type: RTCSdpType;
    sdp: string;
  }

  class RTCIceCandidate {
    constructor(candidateInitDict?: RTCIceCandidateInit);
    candidate: string;
    sdpMLineIndex: number | null;
    sdpMid: string | null;
  }

  interface RTCDataChannelInit {
    ordered?: boolean;
    maxPacketLifeTime?: number;
    maxRetransmits?: number;
    protocol?: string;
    negotiated?: boolean;
    id?: number;
  }

  class RTCDataChannel {
    label: string;
    ordered: boolean;
    maxPacketLifeTime: number | null;
    maxRetransmits: number | null;
    protocol: string;
    negotiated: boolean;
    id: number | null;
    readyState: RTCDataChannelState;
    bufferedAmount: number;

    send(data: string | Blob | ArrayBuffer | ArrayBufferView): void;
    close(): void;

    onopen: (() => void) | null;
    onmessage: ((event: MessageEvent) => void) | null;
    onclose: (() => void) | null;
    onerror: ((event: Event) => void) | null;
  }

  interface RTCPeerConnectionIceEvent {
    candidate: RTCIceCandidate | null;
  }

  interface RTCDataChannelEvent {
    channel: RTCDataChannel;
  }

  type RTCSignalingState = 'stable' | 'have-local-offer' | 'have-remote-offer' | 'have-local-pranswer' | 'have-remote-pranswer' | 'closed';
  type RTCPeerConnectionState = 'new' | 'connecting' | 'connected' | 'disconnected' | 'failed' | 'closed';
  type RTCDataChannelState = 'connecting' | 'open' | 'closing' | 'closed';

  interface RTCOfferOptions {
    voiceActivityDetection?: boolean;
    iceRestart?: boolean;
  }

  interface RTCAnswerOptions {}

  interface MessageEvent {
    data: any;
    origin: string;
    lastEventId: string;
    source: MessageEventSource | null;
    ports: MessagePort[];
  }

  type MessageEventSource = WindowProxy | MessagePort | ServiceWorker;

  interface Event {
    type: string;
    target: EventTarget | null;
    currentTarget: EventTarget | null;
    bubbles: boolean;
    cancelable: boolean;
    defaultPrevented: boolean;
    composed: boolean;
    timeStamp: number;

    preventDefault(): void;
    stopImmediatePropagation(): void;
    stopPropagation(): void;
  }

  interface EventTarget {
    addEventListener(type: string, listener: EventListenerOrEventListenerObject, options?: boolean | AddEventListenerOptions): void;
    dispatchEvent(event: Event): boolean;
    removeEventListener(type: string, listener: EventListenerOrEventListenerObject, options?: boolean | EventListenerOptions): void;
  }

  interface EventListenerOptions {
    capture?: boolean;
  }

  interface AddEventListenerOptions extends EventListenerOptions {
    once?: boolean;
    passive?: boolean;
  }

  type EventListenerOrEventListenerObject = EventListener | EventListenerObject;

  interface EventListener {
    (evt: Event): void;
  }

  interface EventListenerObject {
    handleEvent(object: Event): void;
  }
}

export {};
