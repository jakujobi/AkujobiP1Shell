#!/usr/bin/env bash
set -euo pipefail

BIN="python3 -m akujobip1"

run_exact () {
  local name="$1"; local input="$2"; local expected="$3"
  printf "%s" "$input" | eval "$BIN" >"out_${name}.txt" 2>&1
  diff -u "$expected" "out_${name}.txt"
  echo "PASSED: $name"
}

# 1) exit
cat >exp_exit.txt <<'EOF'
AkujobiP1> Bye!
EOF
run_exact exit "exit" exp_exit.txt

# 2) empty then exit
cat >exp_empty_then_exit.txt <<'EOF'
AkujobiP1> AkujobiP1> Bye!
EOF
run_exact empty_then_exit $'\nexit' exp_empty_then_exit.txt

# 3) unknown command
printf 'defnotcmd\nexit\n' | eval "$BIN" > out_unknown.txt 2>&1 || true
grep -q "defnotcmd: command not found" out_unknown.txt && echo "PASSED: unknown_command"

# 4) quoted args smoke (Linux: printf from coreutils)
printf 'printf "%s %s\n" "a b" c\nexit\n' | eval "$BIN" > /dev/null
echo "PASSED: quoted_args_smoke"
