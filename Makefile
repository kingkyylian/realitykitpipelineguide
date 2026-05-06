PROJECT = RealityKitPipelineDemo.xcodeproj
SCHEME = RealityKitPipelineDemo
DERIVED_DATA = Build/DerivedData
SKILL_NAME = realitykit-pipeline-guide
CODEX_HOME ?= $(HOME)/.codex

.PHONY: generate build validate test doctor status new-asset prompt-asset make-asset build-asset inspect-usdz verify-asset accept-asset guide release-check install-skill clean

generate:
	xcodegen generate

build:
	xcodebuild -quiet -project $(PROJECT) -scheme $(SCHEME) -destination 'generic/platform=iOS Simulator' -derivedDataPath $(DERIVED_DATA) build
	@echo "xcodebuild ok"

validate:
	node -e "JSON.parse(require('fs').readFileSync('Tools/asset_manifest.json','utf8')); console.log('manifest ok')"

test:
	python3 -m unittest discover -s Tests

doctor:
	python3 Tools/rkp.py doctor $(if $(blender),--blender,) $(if $(json),--json,)

status:
	python3 Tools/rkp.py status

new-asset:
	@test -n "$(id)" || (echo "usage: make new-asset id=enemy_drone type=gameplay_target" && exit 2)
	python3 Tools/rkp.py new-asset "$(id)" --type "$(or $(type),prop)"

prompt-asset:
	@test -n "$(id)" || (echo "usage: make prompt-asset id=enemy_drone type=gameplay_target prompt='red flying drone target'" && exit 2)
	@test -n "$(prompt)" || (echo "usage: make prompt-asset id=enemy_drone type=gameplay_target prompt='red flying drone target'" && exit 2)
	python3 Tools/rkp.py prompt-asset "$(id)" --type "$(or $(type),prop)" --prompt "$(prompt)"

make-asset:
	@test -n "$(id)" || (echo "usage: make make-asset id=enemy_drone type=gameplay_target prompt='red flying drone target'" && exit 2)
	@test -n "$(prompt)" || (echo "usage: make make-asset id=enemy_drone type=gameplay_target prompt='red flying drone target'" && exit 2)
	python3 Tools/rkp.py make-asset "$(id)" --type "$(or $(type),prop)" --prompt "$(prompt)" $(if $(build),--build,) $(if $(screenshot),--screenshot "$(screenshot)",) $(if $(release),--release-check,)

build-asset:
	@test -n "$(id)" || (echo "usage: make build-asset id=enemy_drone" && exit 2)
	python3 Tools/rkp.py build-asset "$(id)"

inspect-usdz:
	@test -n "$(id)" || (echo "usage: make inspect-usdz id=enemy_drone" && exit 2)
	python3 Tools/rkp.py inspect-usdz "$(id)" $(if $(json),--json,)

verify-asset:
	@test -n "$(id)" || (echo "usage: make verify-asset id=enemy_drone build=1 screenshot=Docs/screenshots/enemy_drone.jpg release=1" && exit 2)
	python3 Tools/rkp.py verify-asset "$(id)" $(if $(build),--build,) $(if $(screenshot),--screenshot "$(screenshot)",) $(if $(release),--release-check,)

accept-asset:
	@test -n "$(id)" || (echo "usage: make accept-asset id=enemy_drone screenshot=Docs/screenshots/enemy_drone.jpg" && exit 2)
	@test -n "$(screenshot)" || (echo "usage: make accept-asset id=enemy_drone screenshot=Docs/screenshots/enemy_drone.jpg" && exit 2)
	python3 Tools/rkp.py accept-asset "$(id)" --screenshot "$(screenshot)"

guide:
	mkdir -p Build Docs/pdf
	pandoc Docs/guide.md --standalone --embed-resources --resource-path=Docs --css Docs/guide-style.css --metadata title="RealityKit Asset and Texture Pipeline Guide" -o Build/realitykit-pipeline-guide.html
	weasyprint Build/realitykit-pipeline-guide.html Build/realitykit-pipeline-guide.pdf
	cp Build/realitykit-pipeline-guide.pdf Docs/pdf/realitykit-pipeline-guide.pdf

release-check:
	python3 Tools/rkp.py release-check

install-skill:
	mkdir -p "$(CODEX_HOME)/skills/$(SKILL_NAME)"
	cp -R "Skills/$(SKILL_NAME)/." "$(CODEX_HOME)/skills/$(SKILL_NAME)/"
	@echo "installed $(SKILL_NAME) to $(CODEX_HOME)/skills/$(SKILL_NAME)"

clean:
	rm -rf Build/DerivedData
