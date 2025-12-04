import re
import difflib
from lhdiff import LHDiff

class BugIdentifier:
    def __init__(self, commit_history):
        self.commits = commit_history 
        self.bug_inducing_commits = set()

    def identify_fixes(self):
        """
        Scans commit messages for fix keywords.
        """
        fix_keywords = [r"fix", r"bug", r"error", r"issue", r"close #"]
        
        print("\n[Bonus] Scanning for bug fixes...")
        for commit in self.commits:
            msg = commit['msg'].lower()
            if any(re.search(kw, msg) for kw in fix_keywords):
                print(f"  > Fix Commit Found: {commit['id']} | Msg: {commit['msg']}")
                self._trace_back(commit)

    def _trace_back(self, fix_commit):
        """
        Identifies changed lines in the fix and traces them back.
        """
        # 1. Diff the fix to find lines REMOVED (these were the buggy lines)
        prev_lines = fix_commit['file_prev'].splitlines()
        curr_lines = fix_commit['file_curr'].splitlines()
        
        diff = difflib.ndiff(prev_lines, curr_lines)
        buggy_indices_prev = []
        
        idx = 0
        for line in diff:
            if line.startswith('- '): # Line removed in fix -> it was buggy
                buggy_indices_prev.append(idx)
                idx += 1
            elif line.startswith('  '):
                idx += 1
        
        if not buggy_indices_prev:
            print("    (No lines removed in fix, simplified logic skips complex refactors)")
            return

        print(f"    Buggy lines in previous version: {buggy_indices_prev}")
        self._blame(fix_commit['parent_id'], buggy_indices_prev)

    def _blame(self, start_commit_id, target_indices):
        """
        Walks history backwards to find who introduced the lines.
        """
        start_idx = next((i for i, c in enumerate(self.commits) if c['id'] == start_commit_id), -1)
        if start_idx == -1: return

        current_indices = set(target_indices)
        
        # Walk backwards
        for i in range(start_idx, -1, -1):
            commit = self.commits[i]
            
            # Map Current -> Previous to see if line existed before
            tracker = LHDiff(commit['file_prev'], commit['file_curr'])
            mapping = tracker.run()
            
            # Reverse map: New Index -> Old Index
            rev_map = {}
            for old, new_list in mapping.items():
                for n in new_list:
                    rev_map[n] = old
            
            next_indices = set()
            for lines_idx in list(current_indices):
                if lines_idx in rev_map:
                    # Line existed before, keep tracing back
                    next_indices.add(rev_map[lines_idx])
                else:
                    # Line does not map to previous file -> Introduced here!
                    print(f"    !!! BUG ORIGIN FOUND: Commit {commit['id']} introduced buggy line {lines_idx}")
                    self.bug_inducing_commits.add(commit['id'])
                    current_indices.remove(lines_idx)
            
            if not current_indices: break
            current_indices = next_indices