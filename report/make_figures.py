"""Generate all figures used in the final report.

Run from the repository root:  python report/make_figures.py
Output: report/figures/*.png
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Circle, Ellipse

OUT = os.path.join(os.path.dirname(__file__), "figures")
os.makedirs(OUT, exist_ok=True)

NAVY = "#12203d"
STEEL = "#2f4d7d"
TEAL = "#1f7a6b"
AMBER = "#a15c07"
LIGHT = "#eef2fa"
LIGHT2 = "#e8f3f0"
LIGHT3 = "#fdf3e3"
BORDER = "#b9c7de"
GREY = "#5a6478"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 9,
    "axes.linewidth": 0.8,
    "savefig.dpi": 220,
})


def canvas(w=10.0, h=5.6, xlim=(0, 100), ylim=(0, 100)):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.axis("off")
    return fig, ax


def box(ax, x, y, w, h, text, fc=LIGHT, ec=BORDER, fs=8.5, bold=False,
        color=NAVY, rounding=0.02, lw=0.9, align="center"):
    p = FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={rounding}",
                       linewidth=lw, edgecolor=ec, facecolor=fc, zorder=3)
    ax.add_patch(p)
    if text:
        ax.text(x + w / 2, y + h / 2, text,
                ha="center", va="center", fontsize=fs, color=color,
                fontweight="bold" if bold else "normal", zorder=4, linespacing=1.35)
    return p


def arrow(ax, p1, p2, text=None, color=STEEL, style="-|>", rad=0.0, fs=7.4,
          lw=1.1, toff=(0, 1.8), ls="-"):
    a = FancyArrowPatch(p1, p2, arrowstyle=style, mutation_scale=9,
                        linewidth=lw, color=color, linestyle=ls,
                        connectionstyle=f"arc3,rad={rad}", zorder=2,
                        shrinkA=1, shrinkB=1)
    ax.add_patch(a)
    if text:
        mx, my = (p1[0] + p2[0]) / 2 + toff[0], (p1[1] + p2[1]) / 2 + toff[1]
        ax.text(mx, my, text, fontsize=fs, color=GREY, ha="center",
                va="center", zorder=5)


def save(fig, name):
    path = os.path.join(OUT, name)
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("wrote", path)


# --------------------------------------------------------------- Figure 4.1
def architecture():
    fig, ax = canvas(10.2, 6.4)
    ax.text(50, 97.5, "Client tier  —  React 18 + Vite 5 single-page application",
            ha="center", va="center", fontsize=9.5, color=NAVY, fontweight="bold")
    box(ax, 5, 78, 90, 17, "", fc="white", ec=BORDER)
    pages = ["Dashboard\n(stats, activity, health)", "Records\n(issue, revoke, correct)",
             "Students\n(users, courses, grades)", "Student portal\n(own credentials)",
             "Public Verify\n(/verify/:credId, QR)"]
    for i, p in enumerate(pages):
        box(ax, 7 + i * 17.6, 85.5, 16.2, 7.4, p, fc=LIGHT, fs=7.2)
    box(ax, 7, 79.8, 42, 4.6, "Web Crypto SHA-256 · QR codes · shareable links", fc=LIGHT, fs=7.2)
    box(ax, 51, 79.8, 42, 4.6, "MetaMask: personal_sign · eth_sendTransaction", fc=LIGHT3,
        ec="#e0c9a3", fs=7.2)

    arrow(ax, (20, 78), (20, 72.2), "")
    ax.text(19, 75.2, "HTTPS /api", fontsize=7.3, color=GREY, ha="right", va="center")
    arrow(ax, (80, 78), (80, 72.2), "", color=AMBER)
    ax.text(81, 75.2, "wallet-signed transactions", fontsize=7.3, color=GREY, ha="left", va="center")

    ax.text(50, 74.8, "Application tier  —  Node.js 26 + Express 4 REST API (:5001)",
            ha="center", va="center", fontsize=9.5, color=NAVY, fontweight="bold")
    box(ax, 5, 42, 90, 29, "", fc="white", ec=BORDER)
    mods = ["Identity & RBAC\nwallet sessions", "Transcript\ncompiler", "Digest &\ncanonical JSON",
            "Issuer credential\nsignature", "Verification\norchestrator", "Audit trail\n& metrics"]
    for i, m in enumerate(mods):
        box(ax, 7 + i * 14.6, 60.5, 13.2, 7.6, m, fc=LIGHT, fs=7.1)
    box(ax, 7, 47.5, 40, 9.5,
        "MySQL 8  —  source of truth\nusers · programs · courses · enrollments\nacademic_records · audit_logs",
        fc="#f7f9fe", fs=7.2, rounding=0.03)
    box(ax, 51, 47.5, 42, 9.5,
        "Document store: uploads/*.pdf.enc (AES-256-GCM)\nIPFS via Pinata (optional, configured, not exercised)\ntransaction queue: nonce control + receipt checks",
        fc="#f7f9fe", fs=7.2, rounding=0.03)

    arrow(ax, (35, 42), (35, 34.5), "", color=AMBER)
    ax.text(34, 38.5, "signed write: issueRecord / updateRecordStatus / supersedeRecord",
            fontsize=7.2, color=GREY, ha="right", va="center")
    arrow(ax, (65, 34.5), (65, 42), "", color=TEAL)
    ax.text(66, 38.5, "view: verifyRecord (eth_call, 0 gas)", fontsize=7.2, color=GREY,
            ha="left", va="center")

    ax.text(50, 31.5, "Trust layer  —  EVM ledger: AcademicRecordManager.sol (Solidity 0.8.24)",
            ha="center", va="center", fontsize=9.5, color=NAVY, fontweight="bold")
    box(ax, 5, 4, 90, 24, "", fc="#fbfcff", ec=STEEL, lw=1.1)
    fields = ["bytes32\nrecordId", "bytes32\nrecordHash", "string\nipfsCID", "address\nissuer",
              "uint256\nissuedAt", "enum\nstatus", "bytes32\nreplacementId"]
    for i, f in enumerate(fields):
        box(ax, 7 + i * 12.4, 16.5, 11.2, 7.5, f, fc=LIGHT, fs=6.9)
    box(ax, 7, 7.5, 86, 6.0,
        "RBAC: admin + issuer whitelist   ·   lifecycle: Active / Revoked / Superseded   ·   atomic supersession",
        fc="#f4f7fd", fs=7.4)
    ax.text(50, 1.0, "immutable evidence only — no personal data, no grades, no decryption keys on-chain",
            ha="center", fontsize=7.2, color=GREY, style="italic")
    save(fig, "fig-4-1-architecture.png")


# --------------------------------------------------------------- Figure 4.2
def context_dfd():
    fig, ax = canvas(9.8, 5.6)
    box(ax, 40, 39, 26, 20, "Academic Record\nManagement and\nVerification System\n(0)",
        fc=LIGHT, ec=STEEL, fs=9.4, bold=True, rounding=0.06)
    box(ax, 2, 79, 22, 12, "Issuer\n(university registrar /\nfaculty wallet)", fc=LIGHT3, ec="#e0c9a3", fs=8)
    box(ax, 2, 7, 22, 12, "Student / holder\n(credential owner)", fc=LIGHT2, ec="#b7d7cf", fs=8)
    box(ax, 76, 79, 22, 12, "Verifier\n(employer, agency,\nadmissions office)", fc=LIGHT3, ec="#e0c9a3", fs=8)
    box(ax, 76, 7, 22, 12, "EVM ledger + IPFS\n(trust and storage\ninfrastructure)", fc="#f7f9fe", ec=BORDER, fs=8)

    arrow(ax, (24, 84), (42, 59), "")
    ax.text(30, 69, "academic data,\nissue / correct / revoke", fontsize=7.2, color=GREY,
            ha="right", va="center")
    arrow(ax, (44, 57), (25, 81), "")
    ax.text(46, 75, "credential, digest,\ntx receipt", fontsize=7.2, color=GREY, ha="left", va="center")
    arrow(ax, (24, 15), (42, 42), "")
    ax.text(23, 27, "access request,\nshared link", fontsize=7.2, color=GREY, ha="right", va="center")
    arrow(ax, (44, 45), (25, 12), "")
    ax.text(50, 33, "credential file,\nQR link, status", fontsize=7.2, color=GREY, ha="left", va="center")
    arrow(ax, (66, 59), (78, 80), "")
    ax.text(79, 70, "record ID /\npresented document", fontsize=7.2, color=GREY, ha="left", va="center")
    arrow(ax, (78, 79), (63, 57), "")
    ax.text(78, 61, "valid · invalid ·\nrevoked · unavailable", fontsize=7.2, color=GREY, ha="left", va="center")
    arrow(ax, (64, 42), (78, 15), "")
    ax.text(66, 27, "digest, CID,\nissuer, status", fontsize=7.2, color=GREY, ha="right", va="center")
    arrow(ax, (80, 15), (63, 39), "")
    ax.text(81, 33, "anchored evidence /\nread result", fontsize=7.2, color=GREY, ha="left", va="center")
    save(fig, "fig-4-2-context-dfd.png")


# --------------------------------------------------------------- Figure 4.3
def level1_dfd():
    fig, ax = canvas(10.4, 6.0)
    procs = [
        (2, "1. Authenticate\nand authorise"),
        (22, "2. Issue credential\n(compile, hash, sign)"),
        (42, "3. Hold and share\ncredential"),
        (62, "4. Verify record\n(public)"),
        (82, "5. Academic data and\nlifecycle"),
    ]
    for i, (x, t) in enumerate(procs):
        box(ax, x, 66, 14, 14, t, fc=LIGHT, ec=STEEL, fs=7.2, rounding=0.04)

    box(ax, 2, 88, 28, 8, "Issuer / registrar", fc=LIGHT3, ec="#e0c9a3", fs=8)
    box(ax, 41, 88, 16, 8, "Student / holder", fc=LIGHT2, ec="#b7d7cf", fs=8)
    box(ax, 61, 88, 16, 8, "Verifier", fc=LIGHT3, ec="#e0c9a3", fs=8)
    box(ax, 81, 88, 16, 8, "Admin", fc=LIGHT3, ec="#e0c9a3", fs=8)

    arrow(ax, (9, 88), (9, 80.4), "")
    ax.text(10, 84.4, "wallet + signature", fontsize=6.8, color=GREY, ha="left", va="center")
    arrow(ax, (27, 88), (27, 80.4), "")
    ax.text(28, 85.6, "academic data,\nissuance request", fontsize=6.8, color=GREY, ha="left", va="center")
    arrow(ax, (49, 88), (49, 80.4), "")
    ax.text(50, 85.6, "share / download", fontsize=6.8, color=GREY, ha="left", va="center")
    arrow(ax, (69, 88), (69, 80.4), "")
    ax.text(70, 85.6, "record ID or file", fontsize=6.8, color=GREY, ha="left", va="center")
    arrow(ax, (89, 88), (89, 80.4), "")
    ax.text(90, 85.6, "roles, grades,\nrevoke / correct", fontsize=6.8, color=GREY, ha="left", va="center")

    arrow(ax, (16, 73), (22, 73), "")
    ax.text(19, 75, "session", fontsize=6.6, color=GREY, ha="center")
    arrow(ax, (36, 73), (42, 73), "")
    ax.text(39, 75, "issue", fontsize=6.6, color=GREY, ha="center")
    arrow(ax, (56, 73), (62, 73), "")
    ax.text(59, 75, "present", fontsize=6.6, color=GREY, ha="center")

    box(ax, 4, 26, 36, 12,
        "D1  MySQL 8\nusers · programs · courses · enrollments · academic_records · audit_logs",
        fc="#f7f9fe", ec=BORDER, fs=7.0, rounding=0.02)
    box(ax, 44, 26, 20, 12, "D2  Encrypted documents\n+ IPFS objects (CID)", fc="#f7f9fe", ec=BORDER, fs=7.0)
    box(ax, 72, 26, 22, 12, "D3  Blockchain registry\ndigest · CID · status", fc="#f7f9fe", ec=BORDER, fs=7.0)

    arrow(ax, (9, 66), (9, 38.4), "")
    ax.text(10.5, 52, "wallet, role", fontsize=6.9, color=GREY, ha="left", va="center")
    arrow(ax, (29, 66), (29, 38.4), "")
    ax.text(30.5, 44, "record row, digest", fontsize=6.9, color=GREY, ha="left", va="center")
    arrow(ax, (46, 66), (46, 38.4), "")
    ax.text(47.5, 52, "ciphertext, CID", fontsize=6.9, color=GREY, ha="left", va="center")
    ax.plot([69, 69, 78], [66, 57, 57], color=TEAL, lw=1.0, zorder=2)
    arrow(ax, (78, 57), (78, 38.4), "", color=TEAL)
    ax.text(70, 58.4, "eth_call verifyRecord", fontsize=6.9, color=GREY, ha="left", va="center")
    arrow(ax, (89, 66), (89, 38.4), "")
    ax.text(87.5, 52, "anchor / status tx", fontsize=6.9, color=GREY, ha="right", va="center")

    ax.text(50, 17, "Process 2 computes H = SHA-256(C) over the exact finalised bytes and anchors only H, the CID and metadata.",
            ha="center", fontsize=7.0, color=GREY, style="italic")
    ax.text(50, 11, "Reads: process 5 supplies academic data from D1; process 4 compares D1 and D3; process 3 serves stored documents from D2.",
            ha="center", fontsize=7.0, color=GREY, style="italic")
    save(fig, "fig-4-3-level1-dfd.png")


# --------------------------------------------------------------- Figure 4.4
def erdiagram():
    fig, ax = canvas(10.2, 6.2)

    def entity(x, y, w, h, name, rows, fc=LIGHT):
        box(ax, x, y, w, h, "", fc=fc, ec=STEEL)
        ax.add_patch(Rectangle((x, y + h - 4.2), w, 4.2, fc=STEEL, ec=STEEL, zorder=3.5))
        ax.text(x + w / 2, y + h - 2.1, name, ha="center", va="center", color="white",
                fontsize=7.8, fontweight="bold", zorder=4)
        for i, r in enumerate(rows):
            ax.text(x + 1.4, y + h - 6.6 - i * 3.0, r, fontsize=6.7, color=NAVY,
                    va="center", zorder=4)

    entity(2, 71, 27, 23, "programs",
           ["PK id", "program_code  UQ", "program_name", "degree_title", "total_credits"], fc="#f7f9fe")
    entity(2, 34, 27, 32, "users",
           ["PK id", "wallet_address  UQ", "full_name", "email  UQ", "role  ENUM",
            "FK program_id", "department"], fc="#f7f9fe")
    entity(37, 66, 27, 28, "courses",
           ["PK id", "course_code  UQ", "title", "credits", "FK program_id"], fc="#f7f9fe")
    entity(37, 28, 27, 30, "enrollments",
           ["PK id", "FK student_id", "FK course_id", "term", "grade_points", "status  ENUM"], fc="#f7f9fe")
    entity(71, 32, 27, 46, "academic_records",
           ["PK id", "cred_id  UQ", "record_id  UQ", "FK student_id", "FK program_id",
            "term · gpa · credits", "transcript_json", "pdf_hash (anchored)",
            "ipfs_cid · tx_hash", "status  ENUM", "superseded_by", "issuer_signature"], fc="#fffdf7")
    entity(71, 4, 27, 22, "audit_logs",
           ["PK id", "action", "performed_by", "target", "details"], fc="#f7f9fe")

    arrow(ax, (10, 71), (10, 66), "")
    ax.text(11.5, 68.6, "1 : N", fontsize=6.9, color=GREY, ha="left")
    arrow(ax, (29, 83), (37, 83), "")
    ax.text(33, 84.8, "1 : N", fontsize=6.9, color=GREY, ha="center")
    arrow(ax, (29, 49), (37, 49), "")
    ax.text(33, 50.8, "1 : N", fontsize=6.9, color=GREY, ha="center")
    arrow(ax, (50.5, 66), (50.5, 58), "")
    ax.text(52, 62, "1 : N", fontsize=6.9, color=GREY, ha="left")

    ax.plot([64, 67, 67], [46, 46, 60], color=STEEL, lw=1.0, zorder=2)
    arrow(ax, (67, 60), (71, 60), "")
    ax.text(69, 61.8, "1 : N", fontsize=6.9, color=GREY, ha="center")

    ax.plot([16, 16, 67], [34, 25, 25], color=STEEL, lw=1.0, zorder=2)
    ax.plot([67, 67], [25, 38], color=STEEL, lw=1.0, zorder=2)
    arrow(ax, (67, 38), (71, 38), "")
    ax.text(69, 39.8, "1 : N", fontsize=6.9, color=GREY, ha="center")

    arrow(ax, (85, 32), (85, 26), "")
    ax.text(86.5, 29, "1 : N", fontsize=6.9, color=GREY, ha="left")
    ax.text(50, 1.5,
            "InnoDB foreign keys: ON DELETE CASCADE for student-owned rows, ON DELETE SET NULL for reference rows.",
            ha="center", fontsize=7.0, color=GREY, style="italic")
    save(fig, "fig-4-4-er.png")


# --------------------------------------------------------------- Figure 4.5
def usecase():
    fig, ax = canvas(9.6, 6.0)
    ax.add_patch(Rectangle((30, 8), 42, 84, fc="#fbfcff", ec=STEEL, lw=1.0, zorder=1))
    ax.text(51, 89, "Academic Record System", ha="center", fontsize=9,
            color=NAVY, fontweight="bold")

    cases = [
        (51, 81, "Sign in with wallet"),
        (51, 70, "Issue credential"),
        (51, 59, "Revoke / correct credential"),
        (51, 48, "Maintain programmes, courses,\nenrolments and grades"),
        (51, 37, "View / download own credential"),
        (51, 26, "Share credential / QR link"),
        (51, 15, "Verify credential (public)"),
    ]
    for x, y, t in cases:
        ax.add_patch(Ellipse((x, y), 36, 8.4, fc=LIGHT, ec=STEEL, lw=0.9, zorder=3))
        ax.text(x, y, t, ha="center", va="center", fontsize=7.1, color=NAVY, zorder=4)

    def actor(x, y, label):
        ax.add_patch(Circle((x, y + 9.0), 2.1, fc="white", ec=NAVY, lw=1.0, zorder=4))
        ax.plot([x, x], [y + 6.9, y + 1.2], color=NAVY, lw=1.0, zorder=4)
        ax.plot([x - 3.6, x + 3.6], [y + 4.9, y + 4.9], color=NAVY, lw=1.0, zorder=4)
        ax.plot([x, x - 2.8], [y + 1.2, y - 2.8], color=NAVY, lw=1.0, zorder=4)
        ax.plot([x, x + 2.8], [y + 1.2, y - 2.8], color=NAVY, lw=1.0, zorder=4)
        ax.text(x, y - 7.0, label, ha="center", va="center", fontsize=7.6,
                color=NAVY, fontweight="bold")

    actor(11, 74, "Issuer /\nregistrar")
    actor(11, 44, "Admin")
    actor(90, 52, "Student /\nholder")
    actor(90, 20, "Verifier")

    for y in (81, 70, 59):
        arrow(ax, (14.5, 74), (33, y), "", style="-", lw=0.8, color=GREY)
    for y in (81, 48):
        arrow(ax, (14.5, 44), (33, y), "", style="-", lw=0.8, color=GREY)
    for y in (37, 26, 15):
        arrow(ax, (86.5, 52), (69, y), "", style="-", lw=0.8, color=GREY)
    arrow(ax, (86.5, 20), (69, 15), "", style="-", lw=0.8, color=GREY)
    ax.text(50, 3.2, "Wallet sign-in is required by every actor before any authenticated use case; verification itself is anonymous.",
            ha="center", fontsize=6.9, color=GREY, style="italic")
    save(fig, "fig-4-5-use-case.png")


# --------------------------------------------------------------- Figure 4.6
def sequence():
    fig, ax = canvas(10.4, 6.2)
    lanes = [("Issuer\n(browser)", 8), ("React SPA", 26), ("Express API", 45),
             ("MySQL 8", 63), ("IPFS / Pinata", 79), ("EVM registry", 94)]
    top = 96
    for name, x in lanes:
        box(ax, x - 8, top - 7, 16, 7, name, fc=LIGHT, fs=7.2, bold=True)
        ax.plot([x, x], [top - 7, 6], color=BORDER, lw=0.8, linestyle=(0, (4, 3)), zorder=1)

    msgs = [
        (1, 8, 26, 84, "submit academic data + optional PDF"),
        (2, 26, 45, 78, "POST /api/records (session token)"),
        (3, 45, 63, 72, "validate issuer, load grades and programme"),
        (4, 63, 45, 66, "student row + completed enrolments"),
        (5, 45, 45, 60, "compile canonical JSON, H = SHA-256(C)"),
        (6, 45, 63, 54, "INSERT record, status = DRAFT"),
        (7, 45, 79, 48, "pin document -> CID"),
        (8, 45, 94, 42, "issueRecord(id, H, CID) signed tx"),
        (9, 94, 45, 36, "receipt (block number, logs)"),
        (10, 45, 63, 30, "UPDATE status = ACTIVE, tx_hash"),
        (11, 45, 26, 24, "201 record + transcript + QR payload"),
        (12, 26, 8, 18, "credential, verification link, QR"),
    ]
    for n, x1, x2, y, label in msgs:
        if x1 == x2:
            ax.add_patch(FancyArrowPatch((x1, y + 2.0), (x2 + 0.1, y - 1.2), arrowstyle="-|>",
                                         mutation_scale=8, color=STEEL, lw=0.9,
                                         connectionstyle="arc3,rad=-1.4", zorder=3))
            ax.text(x1 + 1.8, y + 2.6, f"{n}. {label}", fontsize=6.9, color=NAVY,
                    va="bottom", ha="left")
        else:
            arrow(ax, (x1, y), (x2, y), f"{n}. {label}", fs=6.8, toff=(0, 1.7), color=STEEL)
    ax.text(50, 3.2, "Failure path: if the transaction fails, the record stays DRAFT with its stored digest and an audit entry; it is never presented as issued.",
            ha="center", fontsize=7.0, color=GREY, style="italic")
    save(fig, "fig-4-6-sequence-issuance.png")


# --------------------------------------------------------------- Figure 4.7
def activity():
    fig, ax = canvas(9.8, 6.4)

    def node(x, y, w, h, t, fc=LIGHT, ec=STEEL):
        box(ax, x, y, w, h, t, fc=fc, ec=ec, fs=7.4, rounding=0.03)

    def diamond(cx, cy, w, h, t):
        pts = [(cx, cy + h / 2), (cx + w / 2, cy), (cx, cy - h / 2), (cx - w / 2, cy)]
        ax.add_patch(plt.Polygon(pts, closed=True, fc=LIGHT3, ec="#c9a26b", lw=0.9, zorder=3))
        ax.text(cx, cy, t, ha="center", va="center", fontsize=6.9, color=NAVY, zorder=4)

    ax.add_patch(Circle((50, 96), 2.4, fc=NAVY, ec=NAVY, zorder=4))
    node(32, 85, 36, 6, "Receive record ID and/or presented document")
    diamond(50, 74, 28, 9, "record known?")
    node(4, 70.5, 22, 7, "NOT FOUND (404)")
    node(38, 62, 24, 6, "compute H of presented bytes")
    diamond(50, 51, 32, 10, "DB digest = chain digest?")
    node(3, 47, 23, 7, "INVALID / TAMPERED")
    diamond(50, 39, 28, 10, "status = Active?")
    node(3, 35, 23, 7, "REVOKED / SUPERSEDED")
    diamond(50, 27, 32, 10, "issuer signature valid?")
    node(3, 23, 23, 7, "INVALID signature")
    node(30, 11, 40, 6.5, "VALID — evidence and status agree", fc=LIGHT2, ec=TEAL)
    node(76, 47, 22, 7, "UNAVAILABLE\n(chain unreachable)", fc="#fff6f6", ec="#d8a0a0")

    arrow(ax, (50, 93.6), (50, 88.4))
    arrow(ax, (50, 85), (50, 78.6))
    arrow(ax, (36, 74), (26, 73.5), "no", fs=7.0, toff=(0, 1.4))
    arrow(ax, (50, 69.5), (50, 68.2), "yes", fs=7.0, toff=(3, 0))
    arrow(ax, (50, 62), (50, 56.2))
    arrow(ax, (34, 51), (26, 50.5), "no", fs=7.0, toff=(0, 1.4))
    arrow(ax, (50, 46), (50, 44.2), "yes", fs=7.0, toff=(3, 0))
    arrow(ax, (36, 39), (26, 38.5), "no", fs=7.0, toff=(0, 1.4))
    arrow(ax, (50, 34), (50, 32.2), "yes", fs=7.0, toff=(3, 0))
    arrow(ax, (34, 27), (26, 26.5), "no", fs=7.0, toff=(0, 1.4))
    arrow(ax, (50, 22), (50, 17.8), "yes", fs=7.0, toff=(3, 0))
    arrow(ax, (66, 74), (76, 50.5), "chain down", fs=7.0, toff=(1, 5), color="#b25b5b", rad=-0.25)
    save(fig, "fig-4-7-activity-verification.png")


# --------------------------------------------------------------- Figure 4.8
def state_machine():
    fig, ax = canvas(9.6, 3.6)
    box(ax, 6, 50, 20, 12, "DRAFT\n(off-chain only)", fc="#fff6e9", ec="#d5b184", fs=8.4, bold=True)
    box(ax, 42, 50, 22, 12, "ACTIVE\n(anchored)", fc=LIGHT2, ec=TEAL, fs=8.4, bold=True)
    box(ax, 76, 72, 20, 12, "REVOKED", fc="#fdf0f0", ec="#d8a0a0", fs=8.4, bold=True)
    box(ax, 76, 28, 20, 12, "SUPERSEDED", fc="#f4f1fb", ec="#b0a3d6", fs=8.4, bold=True)
    box(ax, 40, 12, 26, 10, "corrected successor\n(new ACTIVE record)", fc=LIGHT, ec=STEEL, fs=7.4)
    ax.add_patch(Circle((2.5, 56), 2.0, fc=NAVY, zorder=4))
    arrow(ax, (4.5, 56), (6, 56), "")
    arrow(ax, (26, 58), (42, 58), "")
    ax.text(34, 60, "issue tx", fontsize=7.2, color=GREY, ha="center")
    ax.text(34, 52, "anchor fails:\nretry /anchor", fontsize=7.0, color="#b25b5b", ha="center", va="top")
    arrow(ax, (42, 51), (26, 51), "", color="#b25b5b")
    arrow(ax, (64, 57), (77, 73), "")
    ax.text(63, 77, "updateRecordStatus(1)", fontsize=7.2, color=GREY, ha="right")
    arrow(ax, (64, 55), (77, 37), "")
    ax.text(74, 45, "supersedeRecord(old, new)", fontsize=7.2, color=GREY, ha="right")
    arrow(ax, (84, 28), (66, 21), "")
    ax.text(65, 24.5, "replacementId to successor", fontsize=7.2, color=GREY, ha="right")
    arrow(ax, (53, 22), (53, 50), "", color=TEAL)
    ax.text(50, 2.0, "Transitions are enforced in the contract: only Active records may be revoked or superseded, and an ID can never be re-issued.",
            ha="center", fontsize=7.2, color=GREY, style="italic")
    save(fig, "fig-4-8-state-lifecycle.png")


# --------------------------------------------------------------- Results charts
def load_measurements():
    path = os.path.join(os.path.dirname(__file__), "..", "docs", "measurements.json")
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def chart_latency(m):
    ops = ["Public verification\n(eth_call + DB cross-check)", "Record issuance",
           "Revocation", "Correction\n(atomic supersession)"]
    means = [m["verification"]["meanMs"], m["issuance"]["meanMs"],
             m["revocation"]["ms"], m["supersession"]["ms"]]
    lo = [m["verification"]["meanMs"] - m["verification"]["minMs"],
          m["issuance"]["meanMs"] - m["issuance"]["minMs"], 0, 0]
    hi = [m["verification"]["maxMs"] - m["verification"]["meanMs"],
          m["issuance"]["maxMs"] - m["issuance"]["meanMs"], 0, 0]

    fig, ax = plt.subplots(figsize=(8.6, 3.5))
    y = list(range(len(ops)))
    ax.barh(y, means, color=[TEAL, STEEL, "#6f7fa8", "#6f7fa8"], height=0.55, zorder=3)
    ax.errorbar(means, y, xerr=[lo, hi], fmt="none", ecolor=NAVY, capsize=5, lw=1.0, zorder=4)
    labels = ["54.7 ms (45–69 ms, n=10)", "304 ms (211–384 ms, n=3)", "331 ms (n=1)", "174 ms (n=1)"]
    for i, v in enumerate(means):
        ax.text(v + hi[i] + 12, i, labels[i], va="center", fontsize=8.0, color=NAVY)
    ax.set_yticks(y)
    ax.set_yticklabels(ops, fontsize=8.2)
    ax.invert_yaxis()
    ax.set_xlabel("wall-clock latency (ms) — local Hardhat node, automining", fontsize=8.4)
    ax.set_xlim(0, 520)
    ax.grid(axis="x", color=BORDER, lw=0.6, alpha=0.7, zorder=0)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.set_title("Measured operation latency", fontsize=9.6, color=NAVY, loc="left", pad=8)
    fig.subplots_adjust(left=0.31, right=0.98, top=0.9, bottom=0.16)
    save(fig, "fig-6-1-latency.png")


def chart_gas(m):
    labels = ["Public verification\n(read-only)", "Revocation", "Issuance", "Correction\n(supersession)"]
    vals = [0, m["revocation"]["gasUsed"], m["issuance"]["gasUsed"][0], m["supersession"]["gasUsed"]]
    fig, ax = plt.subplots(figsize=(8.4, 3.3))
    bars = ax.bar(labels, vals, color=[TEAL, "#6f7fa8", STEEL, "#6f7fa8"], width=0.55, zorder=3)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 3200, f"{v:,} gas", ha="center",
                fontsize=8.4, color=NAVY)
    ax.set_ylabel("gas used per operation", fontsize=8.4)
    ax.yaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter("{x:,.0f}"))
    ax.set_ylim(0, max(vals) * 1.22)
    ax.grid(axis="y", color=BORDER, lw=0.6, alpha=0.7, zorder=0)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.set_title("Gas consumption by operation", fontsize=9.6, color=NAVY, loc="left", pad=8)
    fig.tight_layout()
    save(fig, "fig-6-2-gas.png")


def chart_throughput(m):
    t = m["throughput"]
    fig, ax = plt.subplots(figsize=(6.2, 3.2))
    ax.bar(["measured throughput"], [t["txPerSecond"]], color=STEEL, width=0.42, zorder=3)
    ax.axhline(t["targetTxPerSecond"], color=AMBER, lw=1.4, linestyle="--", zorder=4)
    ax.text(-0.44, t["targetTxPerSecond"] + 8, "acceptance target 20 tx/s", color=AMBER,
            fontsize=8.2, ha="left")
    ax.text(0, t["txPerSecond"] + 6,
            f"{t['txPerSecond']} tx/s\n({t['batch']} tx in {t['wallMs']} ms)",
            ha="center", fontsize=8.4, color=NAVY)
    ax.set_ylim(0, 230)
    ax.set_ylabel("transactions per second", fontsize=8.4)
    ax.grid(axis="y", color=BORDER, lw=0.6, alpha=0.7, zorder=0)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.set_title("Issuance throughput against the acceptance target",
                 fontsize=9.6, color=NAVY, loc="left", pad=8)
    fig.tight_layout()
    save(fig, "fig-6-3-throughput.png")


if __name__ == "__main__":
    architecture()
    context_dfd()
    level1_dfd()
    erdiagram()
    usecase()
    sequence()
    activity()
    state_machine()
    m = load_measurements()
    chart_latency(m)
    chart_gas(m)
    chart_throughput(m)
    print("all figures written to", os.path.abspath(OUT))
