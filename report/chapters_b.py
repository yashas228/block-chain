"""Chapters 4-7, references and appendices of the final report."""
import os
import sys

from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt

sys.path.insert(0, os.path.dirname(__file__))
import docx_kit as K  # noqa: E402

FIG = os.path.join(os.path.dirname(__file__), "figures")


def fig(name):
    return os.path.join(FIG, name)


# ---------------------------------------------------------------------- chapter 4
def chapter4(doc):
    K.h1(doc, "4. System Design")

    K.h2(doc, "4.1 Architectural overview")
    K.p(doc, "The system is organised into three tiers and two data planes. The client tier is a "
             "React single-page application with five views; the application tier is an Express REST "
             "API that owns all business logic; the trust tier is an EVM smart contract. The two "
             "data planes are deliberately separated: a relational database holds mutable academic "
             "data and access metadata, while the ledger holds immutable evidence. Figure 4.1 shows "
             "the arrangement, including the two write paths (server-signed and wallet-signed) and "
             "the single read path used by verification.")
    K.figure(doc, fig("fig-4-1-architecture.png"),
             "Three-tier hybrid architecture. Academic data remains in MySQL; only the digest, "
             "storage reference, issuer, timestamp and status are anchored on-chain.", width=6.3)
    K.p(doc, "Three properties of this arrangement matter. First, no personal data crosses into the "
             "trust tier, so the immutability of the ledger does not conflict with the mutability of "
             "academic records. Second, verification is a read: the contract exposes `verifyRecord` "
             "as a `view` function, so the cost of a verification is the cost of an `eth_call`, which "
             "is zero, and the verifier never needs a wallet. Third, the ledger is not on the critical "
             "path of ordinary academic work: grades, enrolments and programme changes are database "
             "operations, and the chain is touched only when a credential is issued or its lifecycle "
             "changes.")

    K.h2(doc, "4.2 Context-level data flow")
    K.p(doc, "Figure 4.2 shows the system as a single process with four external entities. The issuer "
             "supplies academic data and lifecycle instructions and receives credentials and "
             "transaction receipts. The student supplies access and sharing requests and receives "
             "credential files, QR links and status. The verifier supplies an identifier or a "
             "document and receives a verdict. The ledger and storage infrastructure receive "
             "commitments and return anchored evidence.")
    K.figure(doc, fig("fig-4-2-context-dfd.png"),
             "Context-level data flow diagram: external actors and the information exchanged with "
             "the system.", width=6.2)

    K.h2(doc, "4.3 Level-1 data flow")
    K.p(doc, "Figure 4.3 decomposes the system into five processes and three data stores. "
             "Process 1 authenticates a wallet and establishes a session; process 2 compiles, hashes, "
             "signs and encrypts a credential and anchors it; process 3 serves a holder's credentials "
             "and sharing artefacts; process 4 performs public verification; process 5 maintains "
             "academic data and executes lifecycle operations. The stores are the MySQL database "
             "(D1), the encrypted document store with optional IPFS objects (D2), and the on-chain "
             "registry (D3).")
    K.figure(doc, fig("fig-4-3-level1-dfd.png"),
             "Level-1 data flow diagram: processes, data stores and the principal flows between "
             "them.", width=6.3)
    K.p(doc, "Process 2 is where the integrity rule is enforced: it computes H = SHA-256(C) over the "
             "exact finalised bytes C — the uploaded PDF when one is supplied, otherwise the "
             "canonical JSON — and anchors H together with a storage reference and status. Process 4 "
             "recomputes the digest only when content is presented, and otherwise reports the anchored "
             "status. Process 5 is the only writer of lifecycle transitions, and it does so through "
             "the contract rather than by editing the database alone.")

    K.h2(doc, "4.4 Data model")
    K.p(doc, "Figure 4.4 shows the relational model, which has six tables. `programs` and `courses` describe the academic "
             "catalogue, `users` holds identities and roles keyed by wallet address, `enrollments` "
             "records a grade per student per course per term, `academic_records` stores the "
             "finalised credential and its anchored digest, and `audit_logs` records actions with the "
             "wallet that performed them. Foreign keys use `ON DELETE CASCADE` for student-owned rows "
             "and `ON DELETE SET NULL` for reference rows, so that removing a student removes their "
             "records while removing a programme does not.")
    K.figure(doc, fig("fig-4-4-er.png"),
             "Entity–relationship model of the MySQL schema, with primary keys, unique keys and "
             "foreign keys.", width=6.3)
    K.p(doc, "Two details of `academic_records` deserve comment. `transcript_json` stores the exact "
             "canonical document that was hashed, which makes it possible to re-derive the digest and "
             "to show a holder what was signed. `pdf_hash` stores the anchored SHA-256 digest as "
             "0x-prefixed hex, matching the contract's `bytes32` field. The `record_id` column holds "
             "keccak256(credId), i.e. the 32-byte key used by the contract, so that a human identifier "
             "such as `CRED-2026-037` can be mapped deterministically to a ledger key.")
    K.table(doc,
            ["Table", "Purpose", "Key columns"],
            [["programs", "Degree programmes and credit requirements",
              "program_code (UQ), degree_title, total_credits"],
             ["users", "Identities and role assignment",
              "wallet_address (UQ), email (UQ), role ENUM, program_id (FK)"],
             ["courses", "Course catalogue", "course_code (UQ), credits, program_id (FK)"],
             ["enrollments", "Per-term enrolment and grade",
              "student_id (FK), course_id (FK), term, grade, grade_points, status"],
             ["academic_records", "Finalised credential and anchored evidence",
              "cred_id (UQ), record_id (UQ), transcript_json, pdf_hash, ipfs_cid, tx_hash, status, "
              "superseded_by, issuer_signature"],
             ["audit_logs", "Append-only activity trail",
              "action, performed_by, target, details, created_at"]],
            "Relational schema summary.",
            widths=[1.35, 2.5, 2.65], font_size=8.8)

    K.h2(doc, "4.5 On-chain data model and contract interface")
    K.p(doc, "The contract stores one struct per credential, keyed by a 32-byte identifier. The "
             "struct contains the digest, the storage reference, the issuing wallet, the issuance "
             "timestamp, the status enumeration and a replacement identifier. Status is an enum with "
             "three values — Active, Revoked and Superseded — which makes invalid transitions "
             "expressible as preconditions rather than conventions.")
    K.table(doc,
            ["Member", "Type", "Meaning"],
            [["recordId (key)", "bytes32", "keccak256 of the human credential identifier"],
             ["recordHash", "bytes32", "SHA-256 digest of the exact finalised credential bytes"],
             ["ipfsCID", "string", "Content identifier of the stored document (may be empty)"],
             ["issuer", "address", "Wallet that signed the anchoring transaction"],
             ["issueTimestamp", "uint256", "Block timestamp at anchoring"],
             ["status", "enum", "Active, Revoked or Superseded"],
             ["replacementId", "bytes32", "Identifier of the successor record when superseded"]],
            "On-chain credential record.",
            widths=[1.3, 0.9, 4.3], font_size=8.8)
    K.table(doc,
            ["Function", "Access", "Behaviour"],
            [["issueRecord(id, hash, cid)", "Only issuer or admin",
              "Creates an Active record; rejects an identifier that already exists"],
             ["updateRecordStatus(id, status, replacement)", "Only issuer or admin",
              "Changes the status of an Active record; rejects any other prior state"],
             ["supersedeRecord(oldId, newId, newHash, newCid)", "Only issuer or admin",
              "Creates the corrected record and retires the old one in one transaction"],
             ["verifyRecord(id)", "Anyone (view, zero gas)",
              "Returns the full record; reverts for an unknown identifier"],
             ["recordExists(id)", "Anyone (view)",
              "Non-reverting existence probe used by the interface and the API"],
             ["setIssuer(address, enabled)", "Only admin", "Grants or revokes issuance rights"],
             ["transferAdmin(address)", "Only admin", "Transfers administrative control"]],
            "Contract interface (abridged).",
            widths=[2.35, 1.35, 2.8], font_size=8.6)

    K.h2(doc, "4.6 Credential representation and the hashing rule")
    K.p(doc, "A credential is a JSON document compiled from live academic data at the moment of "
             "issuance. It carries the credential identifier, a schema reference, the credential "
             "type, the student's identity and wallet, the programme and degree, the term, the "
             "completed courses with credits and grades, the computed GPA and the total credits "
             "earned. Students are identified by internal identifier and wallet address rather than "
             "by e-mail, so that the document does not leak contact details that the verifier does "
             "not need.")
    K.p(doc, "Because JSON object ordering is not significant but byte order is, the document is "
             "serialised with keys sorted recursively before hashing. The resulting string is the "
             "canonical form; both issuance and verification use the same procedure, and the browser "
             "uses the same rule. Where a PDF is supplied, the PDF's exact bytes are hashed instead "
             "and the canonical JSON is retained as the descriptive record. This addresses a subtle "
             "failure mode that the literature does not always make explicit: a structured transcript "
             "and its rendered PDF are different representations and must never be treated as the "
             "same hash input.")
    K.code_block(doc,
                 "// Canonical JSON: object keys are sorted recursively, so any client that\n"
                 "// rebuilds the same document derives the same digest.\n"
                 "function canonicalJSON(value) {\n"
                 "  const sort = (v) => {\n"
                 "    if (Array.isArray(v)) return v.map(sort);\n"
                 "    if (v && typeof v === 'object') {\n"
                 "      return Object.keys(v).sort().reduce((acc, k) => {\n"
                 "        acc[k] = sort(v[k]);\n"
                 "        return acc;\n"
                 "      }, {});\n"
                 "    }\n"
                 "    return v;\n"
                 "  };\n"
                 "  return JSON.stringify(sort(value));\n"
                 "}\n"
                 "\n"
                 "const canonical    = canonicalJSON(transcript);\n"
                 "const documentBytes = pdfBase64\n"
                 "  ? Buffer.from(pdfBase64, 'base64')   // exact issued bytes\n"
                 "  : Buffer.from(canonical, 'utf8');    // canonical JSON fallback\n"
                 "const digest  = sha256Hex(documentBytes);\n"
                 "const chainId = recordIdOf(credId);    // keccak256(credId)")
    K.p(doc, "Read literally, the rule is: H = SHA-256(C), where C is the exact finalised credential "
             "file; the identifier used on-chain is keccak256(credId); and a rendered PDF and its "
             "JSON source are distinct artefacts with distinct digests. An identifier lookup alone "
             "therefore reports status and evidence but cannot authenticate the contents of a "
             "separately presented document; only a digest comparison can do that.")

    K.h2(doc, "4.7 UML models")

    K.h3(doc, "4.7.1 Use case view")
    K.p(doc, "Figure 4.5 shows the operations available to each actor. Issuers and administrators "
             "share the record-management use cases because both roles are permitted to issue; the "
             "distinction is that the administrator additionally manages the issuer whitelist. "
             "Students see only their own credentials and the sharing controls. Verification is "
             "available to everyone, including anonymous visitors, because it is a read-only query.")
    K.figure(doc, fig("fig-4-5-use-case.png"),
             "Use case diagram. Wallet sign-in precedes every authenticated use case; verification "
             "itself is anonymous.", width=6.1)

    K.h3(doc, "4.7.2 Issuance sequence")
    K.p(doc, "The successful issuance path is shown in Figure 4.6. The issuer submits a student, a "
             "term and optionally a PDF. The API validates the session and the issuer role, loads "
             "completed enrolments, compiles the canonical document, hashes it, inserts a DRAFT row, "
             "optionally pins the document to IPFS, and sends the anchoring transaction. Only after "
             "the receipt arrives does it update the row to ACTIVE and audit the action. When the "
             "issuer's wallet is whitelisted on-chain, the transaction is returned to the browser "
             "unsigned instead, and the client confirms it afterwards.")
    K.figure(doc, fig("fig-4-6-sequence-issuance.png"),
             "Sequence diagram for credential issuance, including the durable DRAFT state that "
             "protects against partial failure.", width=6.3)
    K.p(doc, "The failure path is part of the design rather than an afterthought. If validation, "
             "upload or signing fails, no record is created. If the transaction fails after the row "
             "is written, the record remains DRAFT with its digest and storage reference intact, an "
             "`RECORD_ANCHOR_FAILED` entry is written to the audit log, and the operator can retry "
             "anchoring without re-issuing the credential. A failed transaction can never be "
             "presented as an issued credential, which is the property the midterm acceptance "
             "criteria demanded.")

    K.h3(doc, "4.7.3 Verification activity")
    K.p(doc, "Figure 4.7 shows the verification decision procedure. The system first establishes "
             "whether the identifier is known to either source; if neither the database nor the "
             "ledger knows it, the answer is 404. If content is presented, the digest is recomputed "
             "and compared with both stored digests. The status is then checked, followed by the "
             "issuer signature. A ledger failure suspends the decision and reports the service as "
             "unavailable rather than producing a negative verdict.")
    K.figure(doc, fig("fig-4-7-activity-verification.png"),
             "Activity diagram for verification, showing the distinct outcomes and the "
             "unavailability branch.", width=5.9)

    K.h3(doc, "4.7.4 Lifecycle state machine")
    K.p(doc, "Figure 4.8 shows the state machine. Records move from DRAFT to ACTIVE on confirmation, and from ACTIVE to either REVOKED "
             "or SUPERSEDED. Supersession creates the successor record in the same transaction and "
             "links the predecessor to it, which is what allows a verifier holding an older copy to "
             "discover the correction. Transitions out of a terminal state are rejected by the "
             "contract, and an identifier can never be re-issued, so history cannot be rewritten.")
    K.figure(doc, fig("fig-4-8-state-lifecycle.png"),
             "Credential lifecycle. Terminal states are enforced by contract preconditions.", width=6.1)

    K.h2(doc, "4.8 Security design")
    K.p(doc, "The threat model assumes an attacker who can read the public interface, present forged "
             "documents, attempt to call the API with a wallet they control, and — in the strongest "
             "case tested — modify the database directly. It does not assume an attacker who "
             "controls the contract administrator's key, because that key is the root of trust.")
    K.table(doc,
            ["Threat", "Mitigation", "Evidence"],
            [["Forged or edited credential document",
              "SHA-256 digest anchored at issuance and recomputed at verification",
              "23/23 mutations rejected"],
             ["Unauthorised issuance",
              "Role check in the API and an independent issuer whitelist in the contract",
              "Contract RBAC tests; API 403 tests"],
             ["Database modified behind the ledger",
              "Verification compares database digest and status with the ledger and reports a "
              "consistency flag", "Tamper suite database case"],
             ["Session forgery",
              "Token carries the wallet signature of the login message; the signature is re-verified "
              "on every request", "API authentication tests"],
             ["Replay of an old session",
              "Twelve-hour expiry embedded in the signed message and checked on use",
              "API authentication tests"],
             ["Document theft from disk",
              "AES-256-GCM encryption at rest with a key held outside the database",
              "Ciphertext-on-disk assertion"],
             ["Transaction substitution during client signing",
              "Receipt is checked for status, emitting contract and expected record identifier",
              "API client-signing tests"],
             ["Nonce races under concurrent issuance",
              "Serialised write queue with explicit pending nonce and bounded retries",
              "Throughput and issuance tests"]],
            "Threat model and mitigations.",
            widths=[1.75, 2.95, 1.8], font_size=8.7)

    K.h2(doc, "4.9 Failure semantics")
    K.p(doc, "One of the design decisions that most affects trustworthiness is the vocabulary of "
             "failure. A verifier who is told “invalid” because the RPC endpoint was down will "
             "wrongly reject a genuine credential; a verifier who is told “valid” because the "
             "database row exists has learned nothing about the ledger. The API therefore returns "
             "distinct, documented outcomes, and the interface renders each with different language "
             "and colour.")
    K.table(doc,
            ["Outcome", "Trigger", "HTTP status", "Reported to the verifier"],
            [["Not found", "Identifier unknown to database and ledger", "404",
              "No academic record exists for this identifier"],
             ["Valid", "Digest matches and status is Active", "200",
              "Evidence and status agree; issuer signature verified"],
             ["Tampered", "Presented digest differs from the anchored digest", "200",
              "Integrity check failed; content does not match the anchored record"],
             ["Revoked / superseded", "Anchored status is not Active", "200",
              "Credential is no longer valid; successor shown when present"],
             ["Inconsistent", "Database and ledger disagree", "200",
              "Sources disagree; treat as unverified and investigate"],
             ["Unavailable", "Ledger unreachable", "200 with `chainAvailable: false`",
              "Cannot verify right now; this is not evidence of tampering"]],
            "Verification outcomes and their meaning.",
            widths=[1.1, 2.35, 1.1, 1.95], font_size=8.7)

    K.h2(doc, "4.10 Key design decisions")
    K.table(doc,
            ["Decision", "Alternative considered", "Rationale"],
            [["Anchor a digest, not the document", "Store the PDF or JSON on-chain",
              "Keeps personal data off the ledger and makes cost independent of document size"],
             ["Keep MySQL as the source of truth", "Make the ledger the primary store",
              "Academic data is mutable; a ledger cannot support corrections without destroying history"],
             ["Model correction as supersession", "Edit the record in place",
              "Preserves the audit trail and lets a verifier holding an old copy discover the change"],
             ["Expose verification as a view function", "A write that records the verification",
              "Zero gas, no wallet, no incentive to gate access, and no personal data in the query"],
             ["Require confirmation before ACTIVE", "Optimistic update on submission",
              "Prevents a failed transaction from appearing as an issued credential"],
             ["Cross-check two sources", "Trust the ledger alone",
              "Detects database tampering and exposes disagreement instead of hiding it"],
             ["Support wallet signing with a server fallback", "Server signing only",
              "Demonstrates that the issuer's own key can author the transaction while keeping the "
              "demo usable without a whitelisted wallet"]],
            "Principal design decisions and trade-offs.",
            widths=[1.75, 1.8, 2.95], font_size=8.7)


# ---------------------------------------------------------------------- chapter 5
def chapter5(doc):
    K.h1(doc, "5. Implementation")

    K.h2(doc, "5.1 Repository structure")
    K.p(doc, "The repository is an npm workspace with three areas: the contract and its Hardhat "
             "configuration at the root, a `backend` workspace for the API, and a `client` workspace "
             "for the React application. Test and measurement scripts live in `scripts/`, and their "
             "outputs are committed under `docs/` so that results can be inspected without "
             "re-running the system.")
    K.table(doc,
            ["Path", "Contents"],
            [["contracts/AcademicRecordManager.sol", "State registry with RBAC, lifecycle and verification"],
             ["scripts/deploy.js, role-wallets.js", "Deployment, role wallet funding and issuer whitelisting"],
             ["scripts/smoke-chain.js, smoke-api.js", "Chain-layer and end-to-end assertion suites"],
             ["scripts/tamper-suite.js, chain-outage.js", "Adversarial mutation suite and failure-path test"],
             ["scripts/measure.js", "Latency, gas and throughput measurement to `docs/measurements.json`"],
             ["backend/server.js", "Express application, health and activity endpoints, error handling"],
             ["backend/chain.js", "Provider, ABI, hashing, canonical JSON, transaction queue, client-tx confirmation"],
             ["backend/credential.js", "Issuer signature creation and verification"],
             ["backend/storage.js", "AES-256-GCM document storage and retrieval"],
             ["backend/middleware/auth.js", "Stateless wallet-signature sessions and role guards"],
             ["backend/routes/*.js", "auth, users, academics, records, verify, ipfs and chain endpoints"],
             ["backend/schema.sql, dbInit.js, seed.js", "Schema creation, in-place upgrades and demo data"],
             ["client/src/*", "React application, API client, wallet helpers, pages and design system"],
             ["docs/measurements.json", "Raw measured values used in Chapter 6"]],
            "Repository structure and responsibilities.",
            widths=[2.55, 4.0], font_size=8.7)

    K.h2(doc, "5.2 Smart contract")
    K.p(doc, "The contract is intentionally small: 111 lines of Solidity with no inheritance, no "
             "external calls and no upgradeability. It owns a single administrator address, an issuer "
             "whitelist, and a mapping from identifier to record. Three modifiers encode the "
             "invariants: `onlyAdmin` for whitelist management, `onlyIssuer` for issuance and "
             "lifecycle changes, and `existing` for any operation on a record that must already be "
             "present.")
    K.code_block(doc,
                 "struct AcademicRecord {\n"
                 "    bytes32 recordHash;      // SHA-256 of the canonical transcript / PDF\n"
                 "    string  ipfsCID;         // off-chain storage reference\n"
                 "    address issuer;          // wallet that anchored the record\n"
                 "    uint256 issueTimestamp;  // block timestamp at anchoring\n"
                 "    RecordStatus status;     // Active | Revoked | Superseded\n"
                 "    bytes32 replacementId;   // successor id when superseded\n"
                 "}\n"
                 "\n"
                 "function issueRecord(bytes32 _recordId, bytes32 _recordHash,\n"
                 "                     string calldata _ipfsCID) external onlyIssuer {\n"
                 "    require(records[_recordId].issueTimestamp == 0,\n"
                 "            \"ARM: record id already exists\");\n"
                 "    records[_recordId] = AcademicRecord(_recordHash, _ipfsCID, msg.sender,\n"
                 "        block.timestamp, RecordStatus.Active, bytes32(0));\n"
                 "    emit RecordIssued(_recordId, _recordHash, _ipfsCID, msg.sender);\n"
                 "}\n"
                 "\n"
                 "function supersedeRecord(bytes32 _oldId, bytes32 _newId, bytes32 _newHash,\n"
                 "                         string calldata _newIpfsCID)\n"
                 "    external onlyIssuer existing(_oldId)\n"
                 "{\n"
                 "    require(records[_oldId].status == RecordStatus.Active,\n"
                 "            \"ARM: old record is not active\");\n"
                 "    require(records[_newId].issueTimestamp == 0,\n"
                 "            \"ARM: new record id already exists\");\n"
                 "    records[_newId] = AcademicRecord(_newHash, _newIpfsCID, msg.sender,\n"
                 "        block.timestamp, RecordStatus.Active, bytes32(0));\n"
                 "    records[_oldId].status = RecordStatus.Superseded;\n"
                 "    records[_oldId].replacementId = _newId;\n"
                 "    emit RecordIssued(_newId, _newHash, _newIpfsCID, msg.sender);\n"
                 "    emit RecordStatusUpdated(_oldId, RecordStatus.Superseded, _newId);\n"
                 "}")
    K.p(doc, "Two implementation notes are worth recording. First, `updateRecordStatus` requires the "
             "current status to be Active, which makes double revocation and revocation of a "
             "superseded record impossible rather than merely discouraged. Second, supersession is a "
             "single function rather than two calls from the backend, so there is no window in which "
             "the old record is retired but the corrected one does not yet exist. Both behaviours are "
             "covered by unit tests.")

    K.h2(doc, "5.3 Backend modules")
    K.p(doc, "The API is deliberately thin at the routing layer and concentrates protocol behaviour "
             "in services. `chain.js` owns everything that touches the ledger, including the ABI, the "
             "digest and canonicalisation helpers, the transaction queue and the receipt checks used "
             "by the wallet-signing path. `credential.js` owns the issuer signature. `storage.js` owns "
             "encryption and retrieval of documents. `middleware/auth.js` owns session verification "
             "and role guards. Route modules translate HTTP into calls on these services and are "
             "responsible for status codes and error messages.")
    K.p(doc, "Transactions from the server signer are serialised through an explicit queue. "
             "Concurrent issuance requests would otherwise race for the same account nonce, and "
             "ethers caches RPC responses briefly, which can return a stale nonce. The queue fetches "
             "the pending nonce with a direct `eth_getTransactionCount` call, submits the "
             "transaction, and retries up to three times with a short backoff if the failure message "
             "indicates a nonce conflict. This is a small piece of engineering that materially "
             "affects reliability under load, and it is the reason the throughput measurement in "
             "Section 6.8 is meaningful rather than a measurement of colliding nonces.")

    K.h2(doc, "5.4 Issuance pipeline")
    K.p(doc, "Issuance is the most intricate operation in the system because it spans both data "
             "planes and must remain correct when either one fails. The implementation proceeds in "
             "eight steps:")
    K.bullets(doc, [
        "Validate the session, the role, the student and the term, and check that a record marked "
        "for replacement is currently Active.",
        "Allocate a credential identifier of the form `CRED-<year>-<sequence>`, checking both the "
        "database and the ledger for collisions so that a restored database cannot re-issue an "
        "identifier that is already anchored.",
        "Compile the transcript from completed enrolments, including programme and degree mapping, "
        "weighted GPA and total credits.",
        "Canonicalise the document, or accept the uploaded PDF, and compute the SHA-256 digest.",
        "Encrypt and store the document, and optionally pin it to IPFS, recording the CID.",
        "Insert the record as DRAFT inside a database transaction, with the digest, canonical JSON, "
        "issuer wallet and — on the server path — an issuer signature over the identifier and digest.",
        "Anchor on-chain, either by signing with the server key or by returning an unsigned "
        "transaction request to the browser.",
        "On confirmation, update the row to ACTIVE with the transaction hash and issuance time, mark "
        "the predecessor superseded when applicable, and write an audit entry.",
    ])
    K.p(doc, "The split between steps 6 and 8 is what makes the failure semantics honest: the "
             "credential exists in a durable, non-public state before any transaction is attempted, "
             "and it becomes visible as issued only after the ledger has accepted it. If the process "
             "dies between the two steps, the record is still DRAFT and can be anchored later from "
             "the retry endpoint, which re-signs the credential if the original path did not.")

    K.h2(doc, "5.5 Identity and sessions")
    K.p(doc, "Authentication is password-less. The client requests a challenge for its wallet "
             "address, signs the returned message with `personal_sign`, and posts the signature back. "
             "The API recovers the signer, compares it with the claimed address, checks the expiry "
             "embedded in the message, looks up the wallet and — if it has never been seen — creates "
             "a STUDENT account. The token returned to the client is the base64url encoding of "
             "`{wallet, exp}` concatenated with the signature itself, so no server secret is needed "
             "to validate it: the signature proves wallet ownership and the expiry is inside the "
             "signed payload.")
    K.code_block(doc,
                 "// token = base64url({ wallet, exp }) + \".\" + signature\n"
                 "// message = \"Academic Record System login\\n\"\n"
                 "//           \"wallet: <wallet>\\nexp: <ISO timestamp>\"\n"
                 "function verifyToken(token) {\n"
                 "  const [payloadB64, signature] = token.split('.');\n"
                 "  const { wallet, exp } = JSON.parse(b64urlDecode(payloadB64));\n"
                 "  if (exp * 1000 < Date.now()) return null;\n"
                 "  const recovered = ethers.verifyMessage(buildLoginMessage(wallet, exp), signature);\n"
                 "  return recovered.toLowerCase() === wallet.toLowerCase() ? { wallet, exp } : null;\n"
                 "}")
    K.p(doc, "The trade-off is explicit: the design avoids a server-side session store and a shared "
             "signing secret, at the cost of tokens that cannot be revoked before expiry and that "
             "reveal the wallet address to anyone who sees them. For a twelve-hour academic workflow "
             "this was judged acceptable; a production deployment would add a revocation list or "
             "short-lived tokens with refresh.")

    K.h2(doc, "5.6 Document protection")
    K.p(doc, "Documents are encrypted with AES-256-GCM under a 32-byte key supplied through the "
             "environment. Each file is written as `iv(12 bytes) || authentication tag(16 bytes) || "
             "ciphertext`, so decryption verifies integrity before returning bytes. The key is never "
             "stored in the database and never written to the ledger; if it is absent the system "
             "stores plaintext and says so in the documentation rather than silently pretending to "
             "encrypt. Legacy plaintext files written before encryption was enabled are still served, "
             "which keeps the migration painless at the cost of a small branch in the read path.")

    K.h2(doc, "5.7 Verification pipeline")
    K.p(doc, "Verification is implemented as a single public endpoint with two entry points: by "
             "credential identifier, and by document hash. The second computes the identifier from "
             "the hash and delegates to the first, which keeps the decision logic in one place.")
    K.bullets(doc, [
        "Look up the record in MySQL by credential identifier or ledger key.",
        "Query the ledger with `recordExists` and, when present, fetch the record with "
        "`verifyRecord`. A failure here is captured as a chain error rather than a negative verdict.",
        "If neither source knows the identifier, return 404.",
        "Re-verify the issuer signature over `AcademicRecord:<credId>:<digest>` and record whether "
        "the signer matches the on-chain issuer.",
        "Compare statuses and digests between the two sources and compute a single consistency flag.",
        "Return the database status, ledger status, consistency, signature result, record summary and "
        "raw chain payload.",
    ])
    K.p(doc, "When content is presented, the client hashes it locally with the Web Crypto API and "
             "calls the hash endpoint. This is a deliberate design choice: the document never leaves "
             "the verifier's browser, and the comparison is between a digest the verifier computed "
             "and a digest anchored by the issuer. It also means that a verifier can check a document "
             "obtained from any source, which is the property that makes the system useful outside a "
             "single institution's portal.")

    K.h2(doc, "5.8 Wallet-signed transactions")
    K.p(doc, "The default configuration signs anchoring transactions with a server key, which keeps "
             "the demonstration usable without wallet setup. The system also supports the stronger "
             "model in which the issuer's own wallet signs. A capability endpoint reports whether the "
             "connected wallet is whitelisted on-chain; if it is, the API returns an unsigned "
             "transaction request — target address, encoded calldata and chain identifier — and the "
             "browser submits it through the wallet. The client then posts the transaction hash, and "
             "the API verifies the receipt before promoting the record.")
    K.p(doc, "Receipt verification is not a formality. The API checks that the transaction was mined "
             "within thirty seconds, that it did not revert, that every log was emitted by the "
             "expected contract address, and that one of the logs carries the expected record "
             "identifier. It also requires the credential signature, when supplied, to come from the "
             "account that sent the transaction. Without these checks an attacker could submit a hash "
             "for an unrelated transaction and have the record promoted to ACTIVE.")

    K.h2(doc, "5.9 Client application")
    K.p(doc, "The client is a five-page application with a shared design system, a wallet provider "
             "and a typed API helper. Routes that require a role are guarded; the verification page "
             "is not, because a verifier may be anonymous.")
    K.table(doc,
            ["Page", "Audience", "Function"],
            [["Dashboard", "All signed-in users",
              "Record counts by status, user and academic statistics, recent activity, system health"],
             ["Records", "ADMIN, ISSUER",
              "Issue a credential from a student and term, optionally with a PDF; filter by status; "
              "revoke; issue a correction; copy verification links; show QR codes"],
             ["Students", "ADMIN, ISSUER",
              "Register users, create programmes and courses, enrol students, post grades, manage the "
              "on-chain issuer whitelist"],
             ["Student portal", "STUDENT",
              "Own credentials with status, transcript view, document download, QR and share link"],
             ["Public verify", "Everyone",
              "Lookup by identifier, shared link or dropped document; renders valid, tampered, "
              "revoked, not-found and unavailable outcomes distinctly"]],
            "Client application pages.",
            widths=[1.15, 1.35, 4.05], font_size=8.7)
    K.p(doc, "Two implementation details connect the client to the integrity model. Hashing in the "
             "browser uses `crypto.subtle.digest('SHA-256', bytes)` and formats the result as "
             "0x-prefixed hex, matching the backend exactly, so a digest computed locally can be "
             "compared with an anchored one without server involvement. And the verification page is "
             "driven by the route parameter, so a QR code or a shared link resolves directly to the "
             "result rather than to a search form.")

    K.h2(doc, "5.10 Configuration and deployment")
    K.p(doc, "The system is configured entirely through environment variables, with an example file "
             "that contains placeholders only. Deployment proceeds in five steps: install "
             "dependencies, create and seed the database, start a local node and deploy the "
             "contract, copy the printed contract address and keys into `.env`, and start the API "
             "and client together. The local chain deliberately uses chain ID 31338 rather than "
             "Hardhat's default 31337, so that it does not collide with a wallet's built-in "
             "localhost network entry.")
    K.table(doc,
            ["Variable", "Purpose"],
            [["`PORT`", "API port (default 5000; the project uses 5001 locally)"],
             ["`RPC_URL`", "JSON-RPC endpoint of the EVM node"],
             ["`CONTRACT_ADDRESS`", "Deployed AcademicRecordManager address"],
             ["`SIGNER_PRIVATE_KEY`", "Server signing key and issuer identity for the fallback path"],
             ["`DOCUMENT_ENC_KEY`", "32-byte hex key for AES-256-GCM document encryption"],
             ["`DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`", "MySQL connection settings"],
             ["`PINATA_JWT`, `PINATA_GATEWAY`", "Optional IPFS pinning credentials and gateway"],
             ["`REGISTRATION_CODE`", "Optional invitation code for self-registration"]],
            "Environment configuration.",
            widths=[2.0, 4.55], font_size=8.8)


# ---------------------------------------------------------------------- chapter 6
def chapter6(doc):
    K.h1(doc, "6. Testing and Results")

    K.h2(doc, "6.1 Test strategy")
    K.p(doc, "Testing was organised in four layers, each targeting a different kind of failure. Unit "
             "tests exercise the contract's invariants in isolation. End-to-end API tests exercise "
             "the full stack against a running node, database and API, covering authorisation, "
             "issuance, verification, revocation and supersession. Adversarial tests attempt to "
             "defeat the integrity and failure semantics rather than merely confirm the happy path. "
             "Performance measurement characterises latency, gas and throughput under a documented "
             "configuration. The principle throughout was that a claim in this report must correspond "
             "to an assertion in a script that anyone can run.")
    K.table(doc,
            ["Layer", "Tooling", "Scope", "Result"],
            [["Contract unit", "Hardhat, Mocha, Chai", "RBAC, issuance, duplicates, lifecycle, view functions",
              "14/14 passing"],
             ["Chain service", "Node script", "Issue, verify, supersede and revoke round trip",
              "10/10 assertions"],
             ["End-to-end API", "Node script", "Authentication, roles, issuance, verification, lifecycle, "
              "encryption, client signing, scoping", "52/52 assertions"],
             ["Adversarial", "Tamper suite and outage test", "Document mutation, database tampering, dead RPC",
              "23/23 mutations rejected; 7/7 outage assertions"],
             ["Build", "Vite", "Production client build", "Successful"],
             ["Performance", "Measurement script", "Verification, issuance, revocation, supersession, throughput",
              "Recorded to `docs/measurements.json`"]],
            "Test layers and outcomes.",
            widths=[1.2, 1.35, 2.55, 1.45], font_size=8.6)

    K.h2(doc, "6.2 Test environment")
    K.p(doc, "All results in this chapter were produced on a single developer workstation running "
             "MySQL 8 and a local Hardhat node with automining, chain ID 31338, with the API on port "
             "5001 and the client on port 5174. The measurement run is timestamped in the artefact "
             "(`docs/measurements.json`, 13 October 2026) and records the network description so that "
             "the numbers are not mistaken for public-network performance. Because automining mines a "
             "block per transaction, confirmation latency is at the optimistic end of what any real "
             "network can deliver; the numbers therefore describe implementation overhead, which is "
             "exactly what a prototype can control.")

    K.h2(doc, "6.3 Contract unit tests")
    K.p(doc, "Fourteen tests cover the contract in five groups. They are ordinary assertions rather "
             "than property-based tests, which is a limitation, but they target the invariants that "
             "matter: who may write, what may be written once, and which transitions are legal.")
    K.table(doc,
            ["Group", "Tests", "What is asserted"],
            [["Deployment and RBAC", "4",
              "Deployer becomes admin and issuer; admin can whitelist and de-whitelist; non-admin "
              "cannot; admin transfer works"],
             ["Issuance", "4",
              "All fields stored and event emitted; duplicate identifiers rejected; non-issuer "
              "rejected; whitelisted issuer accepted"],
             ["Lifecycle", "4",
              "Revocation of an active record; rejection on non-active record; rejection for unknown "
              "record; atomic supersession links both records"],
             ["Verification", "2",
              "`verifyRecord` reverts for unknown identifiers; `recordExists` probes without reverting"]],
            "Contract unit test coverage.",
            widths=[1.55, 0.65, 4.35], font_size=8.8, align_center_cols=(1,))

    K.h2(doc, "6.4 Chain service and end-to-end API tests")
    K.p(doc, "The chain-service script exercises the service layer directly: it issues a record, "
             "verifies it, supersedes it, verifies both sides of the link, revokes an active record "
             "and confirms that the state read back matches the state written. Ten assertions cover "
             "the round trip.")
    K.p(doc, "The end-to-end suite is the principal functional evidence. It authenticates with three "
             "role wallets, verifies that unauthenticated access is rejected with 401 and that a "
             "student is refused issuance with 403, loads academic data, issues a credential and "
             "checks both the database row and the ledger entry, checks the issuer signature, performs "
             "public verification with and without a document, downloads the stored PDF and compares "
             "it with the original while confirming that the file on disk is ciphertext, exercises the "
             "wallet-signed issuance path including the whitelisting step, then revokes and supersedes "
             "records and re-checks consistency after each change. Fifty-two assertions pass.")
    K.table(doc,
            ["Area", "Representative assertions"],
            [["Health", "API alive; MySQL connected; EVM node reachable; contract reachable"],
             ["Authentication and RBAC", "Each wallet resolves to its role; unauthenticated access "
              "returns 401; student issuance returns 403; unknown wallet is provisioned as STUDENT"],
             ["Academic data", "Student list and course catalogue load; statistics reflect the seeded data"],
             ["Issuance", "Record ACTIVE in MySQL; transaction anchored; transcript compiled from five "
              "completed courses; GPA computed above 3.0"],
             ["Credential signature", "Signature present, valid, and signed by the issuer wallet"],
             ["Public verification", "Lookup by identifier and ledger key; chain reports Active; database "
              "and chain agree; unknown identifier returns 404"],
             ["Document verification", "PDF record issued and verifiable by hash; a modified copy is not"],
             ["Encrypted storage", "Download equals the original; the file on disk differs from it"],
             ["Client signing", "Capability flips to client mode after whitelisting; wallet-signed "
              "transaction mines; confirmation promotes the record"],
             ["Lifecycle", "Revocation and supersession reflected in both sources; consistency preserved"],
             ["Scoping", "A student cannot read another student's record"]],
            "End-to-end API suite coverage.",
            widths=[1.65, 4.9], font_size=8.7)

    K.h2(doc, "6.5 Tamper suite")
    K.p(doc, "The tamper suite exists because a single flipped byte is a weak demonstration. It issues "
             "a deterministic multi-kilobyte PDF-like document as a control, confirms that the "
             "untouched document verifies, and then submits twenty-three mutated variants. Each "
             "variant is hashed and looked up through the public hash endpoint; anything other than a "
             "404 with `found: false` fails the suite.")
    K.table(doc,
            ["Mutation family", "Count", "Examples"],
            [["Single-bit flips", "16",
              "One bit inverted at positions spread across the header, body and trailer of the document"],
             ["Structural mutations", "6",
              "Truncation by one byte, extension by one byte, corrupted header, zeroed middle block, "
              "completely different file, empty file"],
             ["Forged academic content", "1",
              "Transcript JSON edited (GPA raised, first grade changed) and re-hashed by the attacker"],
             ["Database tampering", "1 scenario, 3 assertions",
              "Digest overwritten directly in MySQL; verification reports the inconsistency while "
              "still showing both sources, and recovers when the original digest is restored"]],
            "Tamper suite composition.",
            widths=[1.7, 1.05, 3.8], font_size=8.7)
    K.p(doc, "All twenty-three mutations were rejected, and the database-tampering case behaved as "
             "designed: the response reported `consistent: false` while still returning the database "
             "status and the ledger status separately, so the mismatch was visible rather than "
             "resolved silently in favour of one source.")

    K.h2(doc, "6.6 Chain-outage test")
    K.p(doc, "The outage test spawns a second API instance configured with an unreachable RPC "
             "endpoint and asserts three behaviours: health reports the database as available and the "
             "chain as unavailable with an explicit error; a known record is still described from the "
             "database with `chainAvailable: false` and without a positive consistency claim; and an "
             "unknown identifier still returns 404 rather than an error. Seven assertions pass. This "
             "is the test that protects the most important promise in the design — that an outage is "
             "never reported as tampering.")

    K.h2(doc, "6.7 Functional behaviour observed in the interface")
    K.p(doc, "The production client build completes without errors. Manual checks covered the "
             "dashboard with live statistics and activity, issuance from live academic data and from "
             "a PDF, status filtering, revocation with confirmation, correction that creates a "
             "linked successor, the student portal with document download and QR code, and the public "
             "verification page for a valid identifier, a shared link, a dropped document, an unknown "
             "identifier and a revoked record. These checks are described as manual because they are "
             "not automated; they are the weakest evidence in this chapter and are recorded as such.")

    K.h2(doc, "6.8 Performance measurement method")
    K.p(doc, "The measurement script authenticates as an issuer and performs each operation a fixed "
             "number of times, timing the full request from the client's perspective and reading gas "
             "from the transaction receipt. Verification is measured over ten trials of "
             "`GET /api/verify/<id>`; issuance over three trials because each issuance anchors a "
             "transaction; revocation and supersession once each, because each is a state change on a "
             "record created for the purpose. Throughput is measured differently: twenty pre-signed "
             "transactions are submitted as a batch and the wall-clock time to completion is recorded, "
             "which isolates submission overhead from wallet or UI latency. The configuration and raw "
             "values are committed, and the number of trials is reported alongside every figure so "
             "that the reader can judge the strength of each estimate.")

    K.h2(doc, "6.9 Measured results")
    K.table(doc,
            ["Operation", "Trials", "Minimum", "Mean", "Maximum", "Gas"],
            [["Public verification", "10", "45 ms", "54.7 ms", "69 ms", "0"],
             ["Issuance", "3", "211 ms", "304 ms", "384 ms", "101,548"],
             ["Revocation", "1", "—", "331 ms", "—", "53,179"],
             ["Correction (supersession)", "1", "—", "174 ms", "—", "150,684"],
             ["Issuance throughput", "20 (batch)", "—", "194.2 tx/s", "—", "101,560 per tx"]],
            "Measured latency and gas consumption on the local Hardhat node.",
            widths=[1.95, 0.85, 0.85, 1.0, 0.9, 1.05], font_size=8.8,
            align_center_cols=(1, 2, 3, 4, 5))
    K.p(doc, "Figures 6.1, 6.2 and 6.3 present the same measurements graphically.")
    K.figure(doc, fig("fig-6-1-latency.png"),
             "Latency by operation, with the observed range where more than one trial was performed.",
             width=6.2)
    K.figure(doc, fig("fig-6-2-gas.png"),
             "Gas consumed by each operation. Verification is a read-only call and consumes none.",
             width=6.2)
    K.figure(doc, fig("fig-6-3-throughput.png"),
             "Issuance throughput against the twenty transactions per second acceptance target.",
             width=5.3)
    K.p(doc, "Three observations follow from the numbers. Verification, the operation a verifier "
             "actually performs, costs nothing and completes in tens of milliseconds, which is the "
             "central economic claim of the design. Issuance is dominated by transaction confirmation "
             "rather than by hashing, encryption or database work, so its cost is a network property "
             "more than an implementation property. And supersession is the most expensive operation "
             "at 150,684 gas because it writes a complete new record and updates the old one in a "
             "single transaction — a deliberate trade of gas for atomicity.")

    K.h2(doc, "6.10 Discussion and threats to validity")
    K.p(doc, "The results support the claim that the implementation meets its objectives, with four "
             "qualifications that should be read as part of the result rather than as caveats added "
             "afterwards.")
    K.bullets(doc, [
        "**Automining inflates latency performance.** A block is produced per transaction, so "
        "confirmation is immediate. On a public network, issuance latency would be governed by block "
        "time and inclusion, not by this code. The measured issuance time should be read as protocol "
        "overhead plus local confirmation, not as a prediction.",
        "**Sample sizes are small.** Ten verification trials and three issuance trials support a "
        "statement about magnitude, not a precise distribution. Revocation and supersession were "
        "measured once each, so their means are single observations and are labelled as such in the "
        "table.",
        "**The tamper suite is systematic but not exhaustive.** Sixteen bit flips and six structural "
        "mutations across a deterministic document exercise the digest boundary thoroughly; they do "
        "not constitute a formal proof, and they say nothing about attacks on the issuer's key.",
        "**Functional coverage is asserted by scripts, usability by observation.** The API and "
        "contract behaviour is checked automatically; the interface was reviewed manually, and "
        "accessibility and cross-browser behaviour were not systematically evaluated.",
    ])
    K.p(doc, "Against the midterm acceptance criteria, the evidence is as follows. Successful issuance "
             "and verification are demonstrated end to end. Rejection of modified content is "
             "demonstrated across twenty-three mutations. Unauthorised writes are rejected by both "
             "the API and the contract, the latter independently of the API. Revocation and "
             "correction behave as specified, including the replacement link. Unavailable-service "
             "responses are distinct from negative verdicts, and the distinction is tested. Timed "
             "operations were repeated under a documented configuration with the number of trials "
             "reported, and the raw values are retained.")

    K.h2(doc, "6.11 Requirements traceability")
    K.table(doc,
            ["Objective", "Evidence in this report"],
            [["O1 — Manage academic records end to end",
              "Sections 5.4, 5.9; API suite (issuance, lifecycle, academic data)"],
             ["O2 — Detect unauthorised modification",
              "Sections 4.6, 5.7; tamper suite 23/23; database-tamper case"],
             ["O3 — Verify without the issuer and without cost",
              "Sections 5.7, 6.9; 54.7 ms mean at 0 gas over ten trials"],
             ["O4 — Preserve the lifecycle",
              "Sections 4.5, 6.3; contract lifecycle tests; API supersession assertions"],
             ["O5 — Give students portable access",
              "Section 5.9; student portal, QR codes and shareable links"],
             ["O6 — Enforce authorisation independently",
              "Sections 4.8, 5.2; contract RBAC tests; API 401/403 assertions"],
             ["O7 — Fail honestly",
              "Sections 4.9, 6.6; outage suite 7/7; 404 semantics preserved"],
             ["O8 — Produce reproducible evidence",
              "Section 6.1 and Appendix B; committed scripts and measurements"]],
            "Traceability from objectives to evidence.",
            widths=[2.35, 4.2], font_size=8.7)


# ---------------------------------------------------------------------- chapter 7
def chapter7(doc):
    K.h1(doc, "7. Conclusion and Future Work")

    K.h2(doc, "7.1 Summary of the work")
    K.p(doc, "This project set out to determine whether a blockchain can make academic credentials "
             "independently verifiable without turning a university's record system into a public "
             "database. The answer delivered here is a qualified yes, and the qualifications are as "
             "informative as the answer. A ledger can hold a commitment that any third party can "
             "check, and can hold the status of that commitment, at a cost of one transaction per "
             "issuance and no cost at all for verification. It cannot hold the credential, cannot "
             "make the credential true, and cannot by itself make the credential portable or "
             "interoperable. Those properties come from the surrounding system: the database that "
             "supplies the data, the signature that binds the issuer to the digest, the storage layer "
             "that protects the document, the API that enforces roles, and the interface that makes "
             "verification a single click for someone who has never heard of a blockchain.")
    K.p(doc, "The implemented system is therefore best described as a student information system with "
             "an anchoring and audit layer attached, rather than as a blockchain application. "
             "Registrars issue, correct and revoke credentials; students hold and share them; "
             "verifiers check them anonymously. The blockchain is present exactly where its "
             "properties are needed and absent everywhere else, which is why the system remains "
             "usable when the chain is slow, and why verification still returns a meaningful, honest "
             "answer when the chain is down.")

    K.h2(doc, "7.2 Conclusions against the objectives")
    K.p(doc, "Objectives O1 to O8 were met to the extent documented in Section 6.11. Records are "
             "managed end to end from live academic data. Modification is detectable through a "
             "digest comparison that requires no issuer involvement, and the tamper suite demonstrates "
             "it across twenty-three mutations. Verification is free and fast — a mean of 54.7 ms at "
             "zero gas — and requires neither an account nor a wallet. The lifecycle is modelled "
             "explicitly, with atomic supersession and a successor link that lets an older copy "
             "discover its replacement. Students can obtain and share their own credentials. "
             "Authorisation is enforced twice, once by the API and once by a contract whitelist that "
             "the API cannot override. Failures are distinguished, and the distinction is tested "
             "against a dead RPC endpoint. Every number in Chapter 6 can be regenerated from the "
             "repository.")
    K.p(doc, "Two objectives were met in a narrower sense than originally imagined. O6 is met at the "
             "level of a single institution: the contract administrator is the ultimate authority, and "
             "in the default configuration that administrator is also the server signer, so the "
             "independence of the two authorisation layers is architectural rather than "
             "organisational. O5 is met for viewing, downloading and sharing, but not for "
             "self-sovereign storage: the student holds a link, not a credential wallet.")

    K.h2(doc, "7.3 Limitations")
    K.p(doc, "The limitations below are stated plainly because a report that hides them would be "
             "less useful than one that does not.")
    K.bullets(doc, [
        "**Network.** All measurements come from a local automining node. Sepolia configuration "
        "exists and the deployment script supports it, but no funded key was available, so "
        "public-network latency and cost are estimated rather than measured.",
        "**Storage.** IPFS pinning is implemented and configured but was not exercised, because no "
        "pinning credential was available. Stored documents are therefore held on the application "
        "server, encrypted, with the CID field left empty in that configuration.",
        "**Standards.** The credential is W3C-VC-shaped but not conformant. The issuer signature is "
        "an EIP-191 message signature over `AcademicRecord:<credId>:<digest>`, not a Data Integrity "
        "proof, and there is no DID document or status list. No interoperability claim is made.",
        "**Trust model.** The administrator controls the issuer whitelist. A compromised "
        "administrative key could whitelist an attacker, although it could not alter records already "
        "anchored. Multi-institution governance is not implemented.",
        "**Privacy.** Personal data is kept off-chain, but a digest on a public ledger is still a "
        "pseudonymous identifier, and repeated issuance to the same student is linkable by an "
        "observer who knows the pattern. Selective disclosure is not implemented.",
        "**Usability.** QR codes are generated and resolve to the verification page, but scanning "
        "requires a third-party application; there is no camera integration and no mobile "
        "application.",
        "**Testing.** Contract tests are example-based rather than property-based, performance "
        "samples are small, and interface verification was manual.",
    ])

    K.h2(doc, "7.4 Future work")
    K.p(doc, "The next steps follow directly from the limitations and from the research gaps "
             "identified in Chapter 2. They are ordered by the value they would add to the system as "
             "it stands.")
    K.bullets(doc, [
        "**W3C Verifiable Credentials and DIDs.** Re-issue credentials as conformant VCs with Data "
        "Integrity proofs, a published issuer DID and a status list, so that a credential issued here "
        "can be consumed by systems built elsewhere.",
        "**Public-network deployment and cost model.** Deploy to Sepolia and then to a Layer 2 "
        "network, measure real confirmation latency and per-credential cost, and publish the cost "
        "model alongside the throughput results.",
        "**Institutional governance.** Replace the single administrator with a multisig or a "
        "consortium arrangement, separate the server signer from the administrative role, and define "
        "the procedure for onboarding and removing issuers.",
        "**Zero-knowledge selective disclosure.** Allow a student to prove properties — a degree was "
        "conferred, a GPA exceeds a threshold — without disclosing the transcript, following the "
        "direction of the ZKBAR-V work.",
        "**Off-chain storage hardening.** Pin encrypted credentials to IPFS with redundancy, monitor "
        "gateway availability, and move decryption keys into a dedicated key service.",
        "**Registrar tooling.** Batch issuance from a CSV extract, cohort statistics, degree audit "
        "checks before issuance, and connectors for existing student information systems.",
        "**Verifier experience.** Camera-based QR scanning, a mobile-friendly progressive web "
        "application with offline verification against cached proofs, and machine-readable "
        "verification endpoints for automated hiring pipelines.",
    ])

    K.h2(doc, "7.5 Closing remarks")
    K.p(doc, "The most useful thing this project produced is not the contract or the API, but a "
             "precise account of where a blockchain helps and where it does not. It helps by making a "
             "commitment public, permanent and cheap to check, and by making the lifecycle of a "
             "credential observable to someone who does not work at the university. It does not help "
             "with data quality, identity, governance, privacy or interoperability, and a system that "
             "pretends otherwise will fail in production while passing its demonstrations. The "
             "implementation described here is small, but it is honest about that boundary: it "
             "anchors what the institution asserts, verifies it without asking the institution, "
             "refuses to call an outage a forgery, and leaves the remaining problems visible for the "
             "next iteration.")


# ---------------------------------------------------------------------- references
def references(doc):
    K.h1(doc, "References")
    items = [
        "Rustemi, A., Dalipi, F., Atanasovski, V., & Risteski, A. (2023). A systematic literature "
        "review on blockchain-based systems for academic certificate verification. *IEEE Access*, 11, "
        "64679–64696. https://doi.org/10.1109/ACCESS.2023.3289598",
        "World Wide Web Consortium. (2025). *Verifiable Credentials Data Model v2.0* (W3C "
        "Recommendation, 15 May 2025). https://www.w3.org/TR/vc-data-model-2.0/",
        "Grech, A., & Camilleri, A. F. (2017). *Blockchain in education*. European Commission Joint "
        "Research Centre, EUR 28778 EN. https://doi.org/10.2760/60649",
        "Blockcerts. (2026). *The open standard for blockchain credentials: introduction, standards "
        "alignment, cert-issuer and verification documentation*. https://www.blockcerts.org/",
        "Blockchain Certificates. (2026). *Cert-issuer and Blockcerts technical documentation* "
        "[GitHub repository]. https://github.com/blockchain-certificates/cert-issuer",
        "A zero-knowledge proof-enabled blockchain-based academic record verification system. (2025). "
        "*Sensors*, 25(11), 3450. https://doi.org/10.3390/s25113450",
        "Turkanović, M., Hölbl, M., Košič, K., Heričko, M., & Kamišalić, A. (2018). EduCTX: A "
        "blockchain-based higher education credit platform. *IEEE Access*, 6, 5112–5127. "
        "https://doi.org/10.1109/ACCESS.2018.2789929",
        "Gräther, W., Kolvenbach, S., Ruland, R., Schütte, J., Torres, C., & Wendland, F. (2018). "
        "Blockchain for education: Lifelong learning passport. *Proceedings of the 1st ERCIM "
        "Blockchain Workshop*. https://doi.org/10.18420/blockchain2018_07",
        "Grech, A., & Camilleri, A. F. (2017). *Blockchain in education* (JRC108255). Publications "
        "Office of the European Union.",
        "Academic certificate verification using blockchain technology. (2025). *2025 IEEE "
        "International Conference on Contemporary Computing and Communications (InC4)*. "
        "https://doi.org/10.1109/InC465408.2025.11256194",
        "Secure academic certificate authentication using blockchain technology. (2025). *9th "
        "International Conference on Computational System and Information Technology for Sustainable "
        "Solutions (CSITSS)*. https://doi.org/10.1109/CSITSS67709.2025.11294218",
        "1EdTech Consortium. (2024–2026). *Open Badges 3.0 specification and conformance "
        "documentation*. https://www.1edtech.org/standards/open-badges",
        "Ethereum Foundation. (2026). *Solidity documentation, version 0.8.24*. "
        "https://docs.soliditylang.org/",
        "Hardhat. (2026). *Hardhat documentation: networks, testing and deployment*. "
        "https://hardhat.org/docs",
        "ethers.js. (2026). *ethers v6 documentation*. https://docs.ethers.org/v6/",
        "Oracle Corporation. (2026). *MySQL 8.0 reference manual*. "
        "https://dev.mysql.com/doc/refman/8.0/en/",
    ]
    for i, item in enumerate(items, start=1):
        para = doc.add_paragraph()
        para.paragraph_format.left_indent = Inches(0.4)
        para.paragraph_format.first_line_indent = Inches(-0.4)
        para.paragraph_format.space_after = Pt(6)
        para.paragraph_format.line_spacing = 1.2
        para.alignment = WD_ALIGN_PARAGRAPH.LEFT
        run = para.add_run(f"[{i}]  ")
        run.bold = True
        run.font.size = Pt(10)
        K.add_rich_text(para, item, size=10)


# ---------------------------------------------------------------------- appendices
def appendices(doc):
    K.h1(doc, "Appendix A — REST API Reference")
    K.table(doc,
            ["Method and path", "Auth", "Purpose"],
            [["POST /api/auth/nonce", "None", "Return the login message to be signed by the wallet"],
             ["POST /api/auth/verify", "None", "Verify the signature, provision unknown wallets, issue a token"],
             ["GET /api/auth/me", "Bearer", "Return the current session's user and role"],
             ["POST /api/auth/session", "None", "Introspect a token and report validity"],
             ["GET /api/users", "Bearer", "List users, optionally filtered by role or query"],
             ["POST /api/users", "None (invite code)", "Register a user with an explicit role"],
             ["PATCH /api/users/:id", "ADMIN", "Update profile, role or department"],
             ["GET /api/academics/programs, /courses", "None", "Read the academic catalogue"],
             ["POST /api/academics/programs, /courses", "ISSUER, ADMIN", "Create catalogue entries"],
             ["GET /api/academics/enrollments", "Bearer", "List enrolments by student or term"],
             ["POST /api/academics/enrollments", "ISSUER, ADMIN", "Enrol a student in a course"],
             ["POST /api/academics/enrollments/:id/grade", "ISSUER, ADMIN", "Post a grade and complete the enrolment"],
             ["GET /api/records", "Bearer", "List records, scoped by role, filterable by status"],
             ["GET /api/records/stats", "Bearer", "Aggregate counts for the dashboard"],
             ["GET /api/records/:credId", "Bearer (owner)", "Record detail with transcript and signature check"],
             ["GET /api/records/:credId/document", "Bearer (owner)", "Download the decrypted credential document"],
             ["POST /api/records", "ISSUER, ADMIN", "Issue or supersede a record (server or client signing)"],
             ["POST /api/records/:credId/confirm", "ISSUER, ADMIN", "Confirm a wallet-signed anchoring transaction"],
             ["POST /api/records/:credId/anchor", "ISSUER, ADMIN", "Retry anchoring a DRAFT record"],
             ["POST /api/records/:credId/status", "ISSUER, ADMIN", "Revoke a record (server or client signing)"],
             ["GET /api/verify/:credId", "None", "Public verification by identifier or ledger key"],
             ["GET /api/verify/hash/:pdfHash", "None", "Public verification by document digest"],
             ["GET /api/verify", "None", "Recent public activity feed"],
             ["POST /api/ipfs/pin", "ISSUER, ADMIN", "Pin an issuer-side asset to IPFS"],
             ["GET /api/chain/capability", "Bearer", "Report whether the wallet may sign transactions itself"],
             ["GET /api/chain/issuers", "Bearer", "List issuer wallets with their on-chain status"],
             ["POST /api/chain/issuers", "ADMIN", "Whitelist or remove an issuer wallet on-chain"],
             ["GET /api/health", "None", "API, database, node and contract reachability"]],
            "REST endpoints implemented by the backend.",
            widths=[2.6, 1.15, 2.8], font_size=8.3)

    K.h1(doc, "Appendix B — Reproducing the Evidence")
    K.p(doc, "The following sequence reproduces every result reported in Chapter 6 on a machine with "
             "Node.js 18 or later and MySQL 8 running locally. Commands are run from the repository "
             "root unless stated otherwise.")
    K.code_block(doc,
                 "# 1. install workspace dependencies\n"
                 "npm install\n"
                 "\n"
                 "# 2. create and seed the database (idempotent)\n"
                 "npm run db:init   -w backend\n"
                 "npm run db:seed   -w backend\n"
                 "\n"
                 "# 3. start a local node and deploy the contract\n"
                 "npx hardhat node --port 8546\n"
                 "npm run deploy:local          # prints CONTRACT_ADDRESS=...\n"
                 "\n"
                 "# 4. configure the environment (see Section 5.10)\n"
                 "cp backend/.env.example .env  # then set the contract address and keys\n"
                 "\n"
                 "# 5. run the application\n"
                 "npm run dev                   # API :5001 and client :5174\n"
                 "\n"
                 "# 6. reproduce the evidence\n"
                 "npx hardhat test              # 14/14 contract unit tests\n"
                 "node scripts/smoke-chain.js   # 10/10 chain-service assertions\n"
                 "node scripts/smoke-api.js     # 52/52 end-to-end assertions\n"
                 "node scripts/tamper-suite.js  # 23/23 mutations rejected\n"
                 "node scripts/chain-outage.js  # 7/7 outage assertions\n"
                 "node scripts/measure.js       # writes docs/measurements.json\n"
                 "npm run build -w client       # production client build")
    K.p(doc, "The measurement script overwrites `docs/measurements.json`, so the committed file is "
             "the record of the run described in this report. The tamper and outage suites require a "
             "seeded database and a running node; the outage suite additionally starts its own API "
             "instance on a separate port with an intentionally unreachable RPC endpoint.")

    K.h1(doc, "Appendix C — Abbreviations")
    K.table(doc,
            ["Abbreviation", "Expansion"],
            [["ABI", "Application Binary Interface"],
             ["API", "Application Programming Interface"],
             ["CID", "Content Identifier (IPFS)"],
             ["DFD", "Data Flow Diagram"],
             ["DID", "Decentralised Identifier"],
             ["ECTS", "European Credit Transfer and Accumulation System"],
             ["EVM", "Ethereum Virtual Machine"],
             ["GPA", "Grade Point Average"],
             ["IPFS", "InterPlanetary File System"],
             ["JSON", "JavaScript Object Notation"],
             ["RBAC", "Role-Based Access Control"],
             ["REST", "Representational State Transfer"],
             ["RPC", "Remote Procedure Call"],
             ["SHA-256", "Secure Hash Algorithm, 256-bit"],
             ["SIS", "Student Information System"],
             ["UML", "Unified Modeling Language"],
             ["VC", "Verifiable Credential"],
             ["ZKP", "Zero-Knowledge Proof"]],
            "Abbreviations used in this report.",
            widths=[1.5, 5.05], font_size=8.8)
