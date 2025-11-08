# RFC: IF.citation Service (v0.1)

## API
- POST /v1/citations  (validate against schema; returns citation_id)
- GET  /v1/citations/{id}
- POST /v1/citations/{id}/verify   (update status, verified_at, verified_by)
- POST /v1/citations/{id}/revoke   (status=revoked; add note)

## Storage
- Content-addressed artifacts (sha256), optional IPFS/S3 pointers
- Graph-friendly lineage (claim→sources→decisions)

## Safety
- No external fetching by default; verifiers run as controlled jobs

## Integration
- yologuard: emit citations alongside manifests
- IF.guard: include citation_ids in decisions

