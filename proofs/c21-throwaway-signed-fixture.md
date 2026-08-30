# ethkey-lite-proof v1
created: 2026-08-30T20:26:20Z
signer: 0x6813Eb9362372EEF6200f3b1dbC3f819671cBA69
sha256: 168ce040b23c38b0579613a2a912b4d8e25bfb8ea926dc44dbae582d1a4537e2
note: c21 negative-control fixture: GENUINE receipt by the PUBLIC throwaway key (pk=3). Signature real, signer NOT a fleet address. Passes bare verify; must fail --require against any fleet address.
signature: 0x89e76c19f9df5ce585ae793cfeb3ef90ab8ac95985f06f6dbb18dddbc39b1d1a22603438a0557d75f352cad6055c0563fd4947274a1ce76ff53ff95b174458ce1b

Signed scope: created + sha256 fields (not the note). Re-verify with
'ethkey.py verify <this file> --require <addr>' or ethers.verifyMessage
on the canonical string:
  ethkey-lite-proof v1\ncreated:<created>\nsha256:<sha256>

-----BEGIN PAYLOAD-----
YzIxIG5lZ2F0aXZlLWNvbnRyb2wgcGF5bG9hZDogYSBnZW51aW5lIHJlY2VpcHQgc2lnbmVkIGJ5
IHRoZSBQVUJMSUMgdGhyb3dhd2F5IGtleSAocGs9MykgZm9yIHRoZSBob29rcGFjayByZXBvLiBT
aWduYXR1cmUgaXMgcmVhbCwgc2lnbmVyIGlzIE5PVCBhIGZsZWV0IGFkZHJlc3MuIE11c3QgcGFz
cyBiYXJlIHZlcmlmeSBhbmQgZmFpbCAtLXJlcXVpcmUgYWdhaW5zdCBhbnkgZmxlZXQgYWRkcmVz
cy4K
-----END PAYLOAD-----
