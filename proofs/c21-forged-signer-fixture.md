# ethkey-lite-proof v1
created: 2026-08-30T20:26:20Z
signer: 0xFD4090e27C1f946Ff01a265cAa7d4ACA662acC15
sha256: adef72fa1084f57d3063b33b514a69dd489e13791351ac87a4863514e01d64a7
note: c21 negative-control fixture: VALID throwaway-key signature (pk=3, public) with a FORGED signer header claiming the A wallet addr. This file is the ATTACK sample, NOT a release receipt. CI asserts every verifier rejects it.
signature: 0xa98fec9994f17c7785f2d8076de6bcbf64d89c88bb8726fda6ac688f337314281acbee06bf794ee09a22c84cadae24297b4648456308bfd78aabf4f99dc474e21b

Signed scope: created + sha256 fields (not the note). Re-verify with
'ethkey.py verify <this file> --require <addr>' or ethers.verifyMessage
on the canonical string:
  ethkey-lite-proof v1\ncreated:<created>\nsha256:<sha256>

-----BEGIN PAYLOAD-----
YzIxIG5lZ2F0aXZlLWNvbnRyb2wgcGF5bG9hZDogYSBWQUxJRCBzaWduYXR1cmUgYnkgdGhlIFBV
QkxJQyB0aHJvd2F3YXkga2V5IChwaz0zKSBzaGlwcGVkIHdpdGggYSBGT1JHRUQgc2lnbmVyIGhl
YWRlciBjbGFpbWluZyB0aGUgQSB3YWxsZXQgYWRkciAoMHhGRDQwLi5hY0MxNSkuIFRoaXMgZmls
ZSBpcyB0aGUgQVRUQUNLIHNhbXBsZSwgbm90IGEgaG9va3BhY2sgcmVjZWlwdC4gRG8gbm90IHRy
dXN0IHRoZSBzaWduZXIgbGluZS4K
-----END PAYLOAD-----
