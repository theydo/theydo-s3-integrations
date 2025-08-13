# Makefile — s3tcli setup (Python 3.12 via micromamba)
SHELL := /usr/bin/env bash

# === Config ==========================================================
# All state stays inside the repo
MAMBA_ROOT := $(CURDIR)/.mamba
MICROMAMBA := $(MAMBA_ROOT)/bin/micromamba
ENV_NAME   := s3tcli
ENV_DIR    := $(MAMBA_ROOT)/envs/$(ENV_NAME)
STAMP      := $(ENV_DIR)/.installed
WRAPPER    := $(CURDIR)/s3tcli

LOG_DIR    := $(CURDIR)/.logs
MAMBA_LOG  := $(LOG_DIR)/mamba.log
PIP_LOG    := $(LOG_DIR)/pip.log

# micromamba flags (ignore user/global condarc)
MMFLAGS  := --rc-file $(CURDIR)/.mambarc
CHANNELS := --override-channels -c conda-forge

# Ensure we do not inherit active conda/mamba env vars (you had (base) in your prompt)
ENV_EXPORT = env -u CONDA_PREFIX -u CONDA_DEFAULT_ENV -u CONDA_SHLVL -u MAMBA_EXE -u MAMBA_ROOT_PREFIX \
                 MAMBA_ROOT_PREFIX="$(MAMBA_ROOT)" CONDA_PKGS_DIRS="$(MAMBA_ROOT)/pkgs"

# Verbosity: default quiet; set VERBOSE=1 to see full solver/pip logs
VERBOSE ?= 0
ifeq ($(VERBOSE),1)
  MAMBA_Q :=
  PIP_Q   :=
  M_REDIRECT :=
  P_REDIRECT :=
else
  MAMBA_Q := -q
  PIP_Q   := -q
  M_REDIRECT := >>"$(MAMBA_LOG)" 2>&1
  P_REDIRECT := >>"$(PIP_LOG)" 2>&1
endif

# Helpers
RUN = $(ENV_EXPORT) "$(MICROMAMBA)" $(MMFLAGS) run -n "$(ENV_NAME)"
PIP = $(RUN) python -m pip

# Colors (disable with NO_COLOR=1)
ifeq ($(NO_COLOR),1)
  BOLD:=
  DIM:=
  RED:=
  GREEN:=
  YELLOW:=
  BLUE:=
  GRAY:=
  RESET:=
else
  BOLD   := \033[1m
  DIM    := \033[2m
  RED    := \033[31m
  GREEN  := \033[32m
  YELLOW := \033[33m
  BLUE   := \033[34m
  GRAY   := \033[90m
  RESET  := \033[0m
endif

# Pretty printers (NOTE: no '@' here so they work mid-line after && / ||)
define step
printf "\n$(BOLD)▸ %s$(RESET)\n" "$(1)"
endef
define ok
printf "$(GREEN)✔$(RESET) %s\n" "$(1)"
endef
define warn
printf "$(YELLOW)⚠$(RESET) %s\n" "$(1)"
endef
define fail
printf "$(RED)✖$(RESET) %s\n" "$(1)"
endef
# ====================================================================

.DEFAULT_GOAL := all
.PHONY: all venv link unlink run shell update doctor clean help

all: venv link
	@printf "\n$(BOLD)Done.$(RESET) Try:  s3tcli --help\n"

# --- Bootstrap micromamba (idempotent) -------------------------------
$(MICROMAMBA): scripts/bootstrap_micromamba.sh | $(LOG_DIR)
	@$(call step,Checking micromamba)
	@bash scripts/bootstrap_micromamba.sh "$(MAMBA_ROOT)" $(M_REDIRECT) \
	  && $(call ok,micromamba ready) \
	  || ( $(call fail,failed to bootstrap micromamba); \
	       printf "See $(BLUE)%s$(RESET)\n" "$(MAMBA_LOG)"; exit 1 )

# --- Create/Update env & pip install (quiet by default) --------------
$(STAMP): environment.yml requirements.txt pyproject.toml | $(MICROMAMBA) $(LOG_DIR)
	@$(call step,Creating/Updating environment [$(ENV_NAME)])
	@set -euo pipefail; \
	if [ -d "$(ENV_DIR)" ]; then \
	  $(ENV_EXPORT) "$(MICROMAMBA)" $(MMFLAGS) $(MAMBA_Q) install -y -n "$(ENV_NAME)" -f environment.yml --root-prefix "$(MAMBA_ROOT)" $(CHANNELS) $(M_REDIRECT); \
	else \
	  $(ENV_EXPORT) "$(MICROMAMBA)" $(MMFLAGS) $(MAMBA_Q) create  -y -n "$(ENV_NAME)" -f environment.yml --root-prefix "$(MAMBA_ROOT)" $(CHANNELS) $(M_REDIRECT); \
	fi
	@$(call ok,conda packages synced)
	@$(call step,Installing Python deps with pip)
	@$(PIP) install $(PIP_Q) --upgrade pip $(P_REDIRECT) \
	  && { [ -s requirements.txt ] && $(PIP) install $(PIP_Q) -r requirements.txt $(P_REDIRECT) || true; } \
	  && $(PIP) install $(PIP_Q) -e . $(P_REDIRECT) \
	  && touch "$(STAMP)" \
	  && $(call ok,pip packages installed) \
	  || ( $(call fail,pip install failed); printf "See $(BLUE)%s$(RESET)\n" "$(PIP_LOG)"; exit 1 )
	@chmod +x "$(WRAPPER)" || true

venv: $(STAMP)

# --- Create/refresh a global 's3tcli' symlink ------------------------
# Prefers /usr/local/bin (macOS/Linux). Falls back to ~/.local/bin if not writable.
link: venv
	@$(call step,Linking global 's3tcli' command)
	@set -euo pipefail; \
	WRAPPER="$(WRAPPER)"; TARGET="/usr/local/bin/s3tcli"; \
	need=1; if [ -L "$$TARGET" ] && [ "$$(readlink "$$TARGET")" = "$$WRAPPER" ]; then need=0; fi; \
	if [ $$need -eq 1 ]; then \
	  if ln -sfn "$$WRAPPER" "$$TARGET" 2>/dev/null; then :; \
	  else if command -v sudo >/dev/null 2>&1; then printf "$(DIM)Using sudo for /usr/local/bin…$(RESET)\n"; sudo ln -sfn "$$WRAPPER" "$$TARGET"; fi; \
	  fi; \
	fi; \
	if command -v s3tcli >/dev/null 2>&1; then \
	  printf "$(GREEN)✔$(RESET) s3tcli on PATH: %s\n" "$$(command -v s3tcli)"; \
	else \
	  printf "$(YELLOW)•$(RESET) '/usr/local/bin' not writable or not on PATH.\n"; \
	  mkdir -p "$$HOME/.local/bin"; ln -sfn "$$WRAPPER" "$$HOME/.local/bin/s3tcli"; \
	  if command -v s3tcli >/dev/null 2>&1; then \
	    printf "$(GREEN)✔$(RESET) s3tcli on PATH: %s\n" "$$(command -v s3tcli)"; \
	  else \
	    printf "$(YELLOW)⚠$(RESET) Add $$HOME/.local/bin to your PATH, then run: s3tcli --help\n"; \
	  fi; \
	fi

unlink:
	@$(call step,Removing global 's3tcli' symlink)
	@set -e; \
	for p in "/usr/local/bin/s3tcli" "$$HOME/.local/bin/s3tcli"; do \
	  if [ -L "$$p" ] && [ "$$(readlink "$$p")" = "$(WRAPPER)" ]; then rm -f "$$p" || sudo rm -f "$$p"; printf "$(GREEN)✔$(RESET) removed %s\n" "$$p"; fi; \
	done || true

# --- Convenience ------------------------------------------------------
run: venv
	@$(RUN) s3tcli $(ARGS)

shell: venv
	@$(RUN) bash -l

update: environment.yml
	@$(ENV_EXPORT) "$(MICROMAMBA)" $(MMFLAGS) install -y -n "$(ENV_NAME)" -f environment.yml --root-prefix "$(MAMBA_ROOT)" $(CHANNELS)

doctor:
	@$(call step,Environment diagnostics)
	@echo "micromamba: $(MICROMAMBA)"; \
	if [ -x "$(MICROMAMBA)" ]; then "$(MICROMAMBA)" --version; fi; \
	$(RUN) python -c "import sys,platform;print(sys.version);print('platform:', platform.platform())"

clean:
	@$(call step,Cleaning)
	@rm -rf "$(MAMBA_ROOT)" "$(LOG_DIR)" && $(call ok,removed .mamba and .logs)

help:
	@printf "$(BOLD)Targets$(RESET)\n  all (default)\n  venv\n  link / unlink\n  run ARGS=...   # run inside env\n  shell          # shell inside env\n  update         # resync conda pkgs\n  doctor         # print versions\n  clean\n"
	@printf "\nUse $(BOLD)VERBOSE=1$(RESET) for full solver/pip output; $(BOLD)NO_COLOR=1$(RESET) to disable colors.\n"

$(LOG_DIR):
	@mkdir -p "$(LOG_DIR)"
