PROJECT = RealityKitPipelineDemo.xcodeproj
SCHEME = RealityKitPipelineDemo
DERIVED_DATA = Build/DerivedData
SKILL_NAME = realitykit-pipeline-guide
CODEX_HOME ?= $(HOME)/.codex

.PHONY: generate build validate doctor new-asset build-asset accept-asset guide release-check install-skill clean

generate:
	xcodegen generate

build:
	xcodebuild -quiet -project $(PROJECT) -scheme $(SCHEME) -destination 'generic/platform=iOS Simulator' -derivedDataPath $(DERIVED_DATA) build
	@echo "xcodebuild ok"

validate:
	node -e "JSON.parse(require('fs').readFileSync('Tools/asset_manifest.json','utf8')); console.log('manifest ok')"

doctor:
	python3 Tools/pipeline_doctor.py

new-asset:
	@test -n "$(id)" || (echo "usage: make new-asset id=enemy_drone type=gameplay_target" && exit 2)
	python3 Tools/new_asset.py --id "$(id)" --type "$(or $(type),prop)"

build-asset:
	@test -n "$(id)" || (echo "usage: make build-asset id=enemy_drone" && exit 2)
	python3 Tools/build_asset.py --id "$(id)"

accept-asset:
	@test -n "$(id)" || (echo "usage: make accept-asset id=enemy_drone screenshot=Docs/screenshots/enemy_drone.jpg" && exit 2)
	@test -n "$(screenshot)" || (echo "usage: make accept-asset id=enemy_drone screenshot=Docs/screenshots/enemy_drone.jpg" && exit 2)
	python3 Tools/accept_asset.py --id "$(id)" --screenshot "$(screenshot)"

guide:
	mkdir -p Build Docs/pdf
	pandoc Docs/guide.md --standalone --embed-resources --resource-path=Docs --css Docs/guide-style.css --metadata title="RealityKit Asset and Texture Pipeline Guide" -o Build/realitykit-pipeline-guide.html
	weasyprint Build/realitykit-pipeline-guide.html Build/realitykit-pipeline-guide.pdf
	cp Build/realitykit-pipeline-guide.pdf Docs/pdf/realitykit-pipeline-guide.pdf

release-check: doctor generate validate build

install-skill:
	mkdir -p "$(CODEX_HOME)/skills/$(SKILL_NAME)"
	cp -R "Skills/$(SKILL_NAME)/." "$(CODEX_HOME)/skills/$(SKILL_NAME)/"
	@echo "installed $(SKILL_NAME) to $(CODEX_HOME)/skills/$(SKILL_NAME)"

clean:
	rm -rf Build/DerivedData
