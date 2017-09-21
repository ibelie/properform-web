declare module goog {
	function provide(name: string): void;
	function require(name: string): void;
	function addDependency(file: string, provide: string[], require: string[], flag: boolean): void;
}

declare module goog.crypt {
	function byteArrayToHex(array: Uint8Array): string;
}

declare module goog.crypt.base64 {
	function decodeStringToUint8Array(str: string): Uint8Array;
	function encodeByteArray(array: Uint8Array): string;
}
