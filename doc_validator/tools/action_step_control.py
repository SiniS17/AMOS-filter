from __future__ import annotations

import re
from pathlib import Path
from datetime import datetime

import pandas as pd


def compute_action_step_control_df(
        df: pd.DataFrame,
        wp_col_candidates=None,
        wo_col_candidates=None,
        workstep_col_candidates=None,
        date_col_candidates=None,
        time_col_candidates=None,
        text_col_candidates=None,
):
    """
    Core logic for Action Step Control operating on a DataFrame.

    Returns:
        asc_df: DataFrame with ActionStepOrderOK + ActionStepIssue columns (filtered to specific columns)
        summary_df: per-WO summary
        wp_value: detected WP (str)
    """
    # 1) defaults for candidate column names (same as in process_action_steps)
    if wp_col_candidates is None:
        wp_col_candidates = ['wp', 'WP', 'wp_header.wpno_i']
    if wo_col_candidates is None:
        wo_col_candidates = ['wo', 'WO', 'WO_NO', 'wo_header.wo']
    if workstep_col_candidates is None:
        workstep_col_candidates = ['Workstep', 'workstep', 'wo_text_action.workstep_linkno_i']
    if date_col_candidates is None:
        date_col_candidates = ['action_date', 'ActionDate', 'date']
    if time_col_candidates is None:
        time_col_candidates = ['action_time', 'ActionTime', 'time']
    if text_col_candidates is None:
        text_col_candidates = ['text', 'wo_text_action.text', 'wo_text_action.action', 'wo_text_action']

    # 2) local helpers copied from your current code
    def _find_column(df_local, candidates):
        if isinstance(candidates, str):
            candidates = [candidates]
        cols_lower = {c.lower(): c for c in df_local.columns}
        for cand in candidates:
            cand_lower = cand.lower()
            if cand_lower in cols_lower:
                return cols_lower[cand_lower]
        for cand in candidates:
            cand_lower = cand.lower()
            for col_l, col_orig in cols_lower.items():
                if cand_lower in col_l:
                    return col_orig
        return None

    def _parse_workstep(v):
        if pd.isna(v) or v is None:
            return None
        s = str(v).strip()
        m = re.search(r'(\d+)', s)
        if not m:
            try:
                return int(s)
            except Exception:
                return None
        return int(m.group(1))

    def _parse_action_datetime(row, date_col='action_date', time_col='action_time'):
        d = row.get(date_col, "")
        t = row.get(time_col, "")
        if (d is None or str(d).strip() == "") and (t is None or str(t).strip() == ""):
            return pd.NaT
        combined = f"{d} {t}".strip()
        return pd.to_datetime(combined, errors='coerce', dayfirst=False)

    def _extract_substep_num(text):
        if text is None:
            return None
        s = str(text).lstrip()
        m = re.match(r'^\s*(\d+)\s*(?:[\/\)\.\-:]|\s+)', s)
        if not m:
            m2 = re.match(r'^\s*(\d+)[\/\)]', s)
            if m2:
                return int(m2.group(1))
            return None
        try:
            return int(m.group(1))
        except Exception:
            return None

    # 3) discover real column names (copy from your existing code)
    real_wp_col = _find_column(df, wp_col_candidates)
    real_wo_col = _find_column(df, wo_col_candidates)
    real_workstep_col = _find_column(df, workstep_col_candidates)
    real_date_col = _find_column(df, date_col_candidates)
    real_time_col = _find_column(df, time_col_candidates)
    real_text_col = _find_column(df, text_col_candidates)

    # 4) same "missing required columns" logic
    missing = []
    if real_wo_col is None:
        missing.append(("wo", wo_col_candidates))
    if real_workstep_col is None:
        missing.append(("Workstep", workstep_col_candidates))
    if real_date_col is None:
        missing.append(("action_date", date_col_candidates))
    if real_time_col is None:
        missing.append(("action_time", time_col_candidates))
    if missing:
        raise ValueError(
            "Required column(s) not found. Tried candidates: "
            + str(missing)
            + ". Columns found: "
            + str(list(df.columns))
        )

    wo_col = real_wo_col
    workstep_col = real_workstep_col
    date_col = real_date_col
    time_col = real_time_col
    wp_col = real_wp_col
    text_col = real_text_col

    # 5) internal compute columns (same as your current code)
    df_work = df.copy()
    df_work['_workstep_num'] = df_work[workstep_col].apply(_parse_workstep)
    df_work['action_datetime'] = df_work.apply(
        lambda r: _parse_action_datetime(r, date_col=date_col, time_col=time_col),
        axis=1,
    )
    if text_col and text_col in df_work.columns:
        df_work['_substep_num'] = df_work[text_col].apply(_extract_substep_num)
    else:
        df_work['_substep_num'] = None

    # 6) initialize result frame (your out_df)
    out_df = df_work.copy()
    out_df['ActionStepOrderOK'] = True
    out_df['ActionStepIssue'] = ""

    # 7) group-by + ordering + violations loop (copy your existing logic)
    summary_rows = []
    grouped = out_df.groupby(wo_col, sort=False)
    for wo, group in grouped:
        idxs = group.index.tolist()
        if len(idxs) <= 1:
            summary_rows.append((wo, len(idxs), 'SKIPPED_SINGLE_STEP', 0))
            continue

        tmp = group[['_workstep_num', '_substep_num', 'action_datetime']].copy()
        tmp['_orig_index'] = tmp.index

        tmp_sorted = tmp.sort_values(
            by=['_workstep_num', '_substep_num', '_orig_index'],
            ascending=[True, True, True],
            na_position='last',
        )

        prev_steps = []
        violations = 0

        for idx in tmp_sorted.index:
            cur_dt = tmp_sorted.at[idx, 'action_datetime']
            cur_ws = tmp_sorted.at[idx, '_workstep_num']
            cur_sub = tmp_sorted.at[idx, '_substep_num']

            if pd.isna(cur_dt):
                out_df.at[idx, 'ActionStepOrderOK'] = False
                prev_issue = out_df.at[idx, 'ActionStepIssue']
                out_df.at[idx, 'ActionStepIssue'] = (
                                                        (prev_issue + '; ') if prev_issue else ''
                                                    ) + 'Missing timestamp'
                violations += 1
            else:
                offending = []
                for p_ws, p_sub, p_dt, p_idx in prev_steps:
                    if pd.isna(p_dt):
                        continue
                    if cur_dt < p_dt:
                        offending.append(p_ws if p_ws is not None else p_idx)

                if offending:
                    offending_unique = []
                    for v in offending:
                        if v not in offending_unique:
                            offending_unique.append(v)
                    offending_readable = [str(v) for v in offending_unique]
                    out_df.at[idx, 'ActionStepOrderOK'] = False
                    out_df.at[idx, 'ActionStepIssue'] = (
                            "Earlier than steps " + ", ".join(offending_readable)
                    )
                    violations += 1

                prev_steps.append((cur_ws, cur_sub, cur_dt, idx))

        summary_rows.append(
            (wo, len(idxs), 'VIOLATIONS' if violations else 'OK', int(violations))
        )

    summary_df = pd.DataFrame(
        summary_rows,
        columns=['wo', 'num_worksteps', 'status', 'num_violations'],
    )

    # 8) detect WP value (no folders yet)
    wp_value = None
    if wp_col and wp_col in out_df.columns:
        non_null_wp = out_df[wp_col].replace('', pd.NA).dropna()
        if not non_null_wp.empty:
            wp_value = non_null_wp.iloc[0]
    if not wp_value:
        wp_value = "No_wp_found"

    # 9) remove internal helper cols before returning
    write_df = out_df.copy()
    for internal_col in ['_workstep_num', 'action_datetime', '_substep_num']:
        if internal_col in write_df.columns:
            write_df.drop(columns=[internal_col], inplace=True)

    # 10) Filter to specific output columns for ActionStepControl sheet
    # Define the columns we want (same as REF/REV but with action_date and ASC result columns)
    asc_output_columns = [
        wo_col,  # WO (discovered column name)
        'WO_state',
        'SEQ',
        workstep_col,  # Workstep (discovered column name)
        'DES',
        'wo_text_action.header',
        'wo_text_action.text',
        date_col,  # action_date (discovered column name)
        time_col,  # action_time (discovered column name)
        'wo_text_action.sign_performed',
        'ActionStepOrderOK',
        'ActionStepIssue'
    ]

    # Filter to only available columns
    available_asc_columns = [col for col in asc_output_columns if col in write_df.columns]
    write_df_filtered = write_df[available_asc_columns].copy()

    return write_df_filtered, summary_df, str(wp_value)


def process_action_steps(
        file_path: str,
        wp_col_candidates=None,
        wo_col_candidates=None,
        workstep_col_candidates=None,
        date_col_candidates=None,
        time_col_candidates=None,
        text_col_candidates=None,
        output_base_dir: str = None,
) -> str:
    """
    File-based wrapper for Action Step Control.

    - Reads the Excel file
    - Calls compute_action_step_control_df(...)
    - Saves a standalone ASC file (same behavior as before, for now)
    """
    fp = Path(file_path)
    if not fp.exists():
        raise FileNotFoundError(f"Input file not found: {file_path}")

    # read as strings to preserve original formatting
    df = pd.read_excel(
        fp,
        engine='openpyxl',
        header=0,
        dtype=str,
        keep_default_na=False,
    )

    # call the core logic
    asc_df, summary_df, wp_value = compute_action_step_control_df(
        df,
        wp_col_candidates=wp_col_candidates,
        wo_col_candidates=wo_col_candidates,
        workstep_col_candidates=workstep_col_candidates,
        date_col_candidates=date_col_candidates,
        time_col_candidates=time_col_candidates,
        text_col_candidates=text_col_candidates,
    )

    # keep your existing folder/file naming for now
    sanitized_wp = re.sub(r'[\\/:*?"<>|]', '_', str(wp_value)).replace(' ', '_')
    if output_base_dir:
        base_dir = Path(output_base_dir)
    else:
        base_dir = Path.cwd()
    result_folder = base_dir / f"{sanitized_wp}_action_step_control"
    result_folder.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = result_folder / f"{sanitized_wp}_action_step_control_{timestamp}.xlsx"

    # The columns are already filtered in compute_action_step_control_df
    # so we can just write asc_df directly
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        asc_df.to_excel(
            writer,
            sheet_name='Results',
            index=False,
        )

        workbook = writer.book
        sheet = writer.sheets['Results']
        sheet.auto_filter.ref = sheet.dimensions

    print(f"✔ Action Step Control result saved:\n{output_file}")
    return str(output_file)