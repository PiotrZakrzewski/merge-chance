from github import Github, PaginatedList
import os
import sys
from datetime import datetime


TOKEN = os.getenv("GH_TOKEN")
# REPORT_PROGRESS controls after how many PRs % of totall processed will be printed out 
REPORT_PROGRESS = 25
EXTRACTION_TS = datetime.now().timestamp()

def main():
    if not TOKEN:
        print("You need to set GH_TOKEN env var")
        sys.exit(1)
    if len(sys.argv) < 2:
        print(
            "Pass github repo name as first position argument.\n 'facebook/react' for example"
        )
        sys.exit(1)

    g = Github(TOKEN)
    target_repo_id = sys.argv[1]
    target_repo = g.get_repo(target_repo_id)
    csv_data = [["state", "created_at", "merged", "merge_date", "no_comments", "extracted_at"]]

    open_prs = target_repo.get_pulls()
    print("Will process open PRs ..")
    open_prs_data = process_pr_data(open_prs)
    csv_data.extend(open_prs_data)

    closed_prs = target_repo.get_pulls(state="closed")
    print("Will process closed PRs ..")
    closed_prs_data = process_pr_data(closed_prs)
    csv_data.extend(closed_prs_data)

    csv_name = f"{target_repo_id}.csv"
    csv_name = csv_name.replace(os.sep, "_")
    print(f"Will write results to {csv_name}")
    with open(csv_name, "w") as outfile:
        lines = [",".join(row) for row in csv_data]
        text = "\n".join(lines)
        outfile.write(text)


def process_pr_data(paginated_gh_result: PaginatedList):
    total = paginated_gh_result.totalCount
    processed_prs = 0
    print(f"{total} PRs to process...")
    rows = []
    for pr in paginated_gh_result:
        created_at = pr.created_at.timestamp() if pr.created_at else "N/A"
        merged_at = pr.merged_at.timestamp() if pr.merged_at else "N/A"
        row = [
            pr.state,
            f"{created_at}",
            f"{pr.merged}",
            f"{merged_at}",
            f"{pr.comments}",
            f"{EXTRACTION_TS}",
        ]
        rows.append(row)
        processed_prs += 1
        if (processed_prs % REPORT_PROGRESS) == 0:
            perc_progress = round(processed_prs / total * 100, 2)
            print(f"Processed {perc_progress} % of PRs")
    print("Processed 100 % of PRs")
    return rows


if __name__ == "__main__":
    main()
