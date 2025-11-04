
import os, re, mailbox, email
from email.header import decode_header, make_header
from email.message import Message
from typing import List, Tuple
import streamlit as st

st.set_page_config(page_title="MBOX Viewer (Gmail-style)", layout="wide")

def dheader(val: str) -> str:
    try:
        return str(make_header(decode_header(val or "")))
    except Exception:
        return val or ""

def get_labels(msg: Message) -> List[str]:
    x = msg.get("X-Gmail-Labels", "") or msg.get("X-Gmail-Labels".lower(), "")
    if not x:
        return []
    # Split respecting quotes
    parts = re.split(r',(?=(?:[^"]*"[^"]*")*[^"]*$)', x)
    out = []
    for p in parts:
        p = p.strip().strip('"')
        if p:
            out.append(p)
    return out

def get_best_body(msg: Message) -> Tuple[str, str]:
    # returns kind ('html' or 'text'), content string
    if msg.is_multipart():
        html_part = None
        text_part = None
        for part in msg.walk():
            ctype = (part.get_content_type() or "").lower()
            disp = (part.get("Content-Disposition") or "").lower()
            if "attachment" in disp:
                continue
            if ctype == "text/html" and html_part is None:
                html_part = part
            elif ctype == "text/plain" and text_part is None:
                text_part = part
        target = html_part or text_part
        if target is None:
            return ("text", "(no body)")
        try:
            payload = target.get_payload(decode=True)
            if payload is None:
                payload = target.get_payload()
                if isinstance(payload, str):
                    return ("html" if (html_part and target is html_part) else "text", payload)
                return ("text", "")
            txt = payload.decode(target.get_content_charset() or "utf-8", errors="replace")
        except Exception:
            txt = target.get_payload(decode=False)
            if not isinstance(txt, str):
                txt = ""
        return ("html" if (html_part and target is html_part) else "text", txt)
    else:
        ctype = (msg.get_content_type() or "").lower()
        try:
            payload = msg.get_payload(decode=True)
            if payload is None:
                payload = msg.get_payload()
                if isinstance(payload, str):
                    return ("html" if ctype=="text/html" else "text", payload)
                return ("text", "")
            txt = payload.decode(msg.get_content_charset() or "utf-8", errors="replace")
        except Exception:
            txt = msg.get_payload(decode=False)
            if not isinstance(txt, str):
                txt = ""
        return ("html" if ctype=="text/html" else "text", txt)

def iter_attachments(msg: Message):
    for part in msg.walk():
        disp = (part.get("Content-Disposition") or "").lower()
        filename = part.get_filename()
        if filename or ("attachment" in disp):
            name = dheader(filename) if filename else "attachment"
            data = part.get_payload(decode=True) or b""
            mime = part.get_content_type() or "application/octet-stream"
            yield name, data, mime

st.title("📥 MBOX Viewer — Gmail-style (Streamlit)")

mbox_path = st.file_uploader("Open a .mbox file", type=["mbox", "mbx", "txt"])

if "index" not in st.session_state:
    st.session_state.index = []  # list of (i, subject, from, to, date, labels)

def build_index(path_or_buffer):
    st.session_state.index = []
    if hasattr(path_or_buffer, "read"):
        # buffer-like; save to temp file for mailbox.mbox
        tmp_path = st.session_state.get("tmp_path", None)
        if not tmp_path:
            tmp_path = os.path.join(st.experimental_get_query_params().get("tmp_dir", [os.getcwd()])[0], "uploaded.mbox")
            st.session_state.tmp_path = tmp_path
        with open(tmp_path, "wb") as f:
            f.write(path_or_buffer.read())
        path = tmp_path
    else:
        path = path_or_buffer

    mbox = mailbox.mbox(path)
    total = len(mbox)
    progress = st.progress(0.0, text=f"Indexing {total} messages…")
    for i, msg in enumerate(mbox):
        subj = dheader(msg.get("subject", "(no subject)"))
        from_ = dheader(msg.get("from", ""))
        to = dheader(msg.get("to", ""))
        date = dheader(msg.get("date", ""))
        labels = get_labels(msg)
        st.session_state.index.append((i, subj, from_, to, date, labels))
        if (i+1) % 50 == 0 or i == total-1:
            progress.progress((i+1)/max(1,total), text=f"Indexed {i+1}/{total}")
    progress.empty()

def open_message(path, idx: int) -> Message:
    mbox = mailbox.mbox(path)
    return mbox[idx]

if mbox_path is not None and st.button("Index file", type="primary"):
    build_index(mbox_path)

if st.session_state.index:
    # Sidebar filters
    with st.sidebar:
        st.subheader("Mailboxes")
        def in_box(lbl): return [it for it in st.session_state.index if lbl in it[5]]
        inbox = len(in_box("Inbox"))
        starred = len(in_box("Starred"))
        sent = len(in_box("Sent"))
        drafts = len(in_box("Drafts"))
        spam = len(in_box("Spam"))
        trash = len(in_box("Trash"))
        box_choice = st.radio("Mailbox", ["All Mail", f"Inbox ({inbox})", f"Starred ({starred})", f"Sent ({sent})", f"Drafts ({drafts})", f"Spam ({spam})", f"Trash ({trash})"], index=0)

        # Labels
        from collections import Counter
        c = Counter()
        for _,_,_,_,_, labs in st.session_state.index:
            for l in labs: c[l]+=1
        st.write("**Labels**")
        chosen_label = st.selectbox("Filter by label", ["(All)"] + [f"{k} ({v})" for k,v in sorted(c.items())], index=0)

        # Search
        query = st.text_input("Search (from, subject)", "")

    # Apply filters
    rows = st.session_state.index
    if box_choice != "All Mail":
        lbl = box_choice.split(" (")[0]
        rows = [r for r in rows if lbl in r[5]]
    if chosen_label != "(All)":
        lbl = chosen_label.rsplit(" (",1)[0]
        rows = [r for r in rows if lbl in r[5]]
    if query:
        ql = query.lower()
        rows = [r for r in rows if (ql in r[1].lower() or ql in r[2].lower())]

    # List + viewer
    import pandas as pd
    df = pd.DataFrame(rows, columns=["#","Subject","From","To","Date","Labels"])
    st.caption(f"{len(rows)} messages")
    clicked = st.dataframe(df[["#","Subject","From","Date","Labels"]], use_container_width=True, height=400, on_select="rerun")

    # Select message by index from input
    selected_idx = st.number_input("Message # to open", min_value=0, max_value=(st.session_state.index[-1][0] if st.session_state.index else 0), step=1, value=(rows[0][0] if rows else 0))

    # Viewer
    if mbox_path is not None and rows:
        msg = open_message(st.session_state.get("tmp_path", "uploaded.mbox"), int(selected_idx))
        subj = dheader(msg.get("subject", "(no subject)"))
        from_ = dheader(msg.get("from", ""))
        to = dheader(msg.get("to", ""))
        date = dheader(msg.get("date", ""))
        msg_id = dheader(msg.get("message-id", ""))
        st.markdown(f"### {subj}")
        st.caption(f"**From:** {from_}  |  **To:** {to}  |  **Date:** {date}  |  **Message-ID:** {msg_id}")

        kind, body = get_best_body(msg)
        if kind == "html":
            st.components.v1.html(body, height=500, scrolling=True)
        else:
            st.text_area("Body (text)", body, height=400)

        atts = list(iter_attachments(msg))
        if atts:
            st.subheader("Attachments")
            for name, data, mime in atts:
                st.download_button(f"Download {name}", data=data, file_name=name, mime=mime)
else:
    st.info("Upload an .mbox and click **Index file** to begin.")
