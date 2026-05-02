PROJECT = RealityKitPipelineDemo.xcodeproj
SCHEME = RealityKitPipelineDemo
DERIVED_DATA = Build/DerivedData
SKILL_NAME = realitykit-pipeline-guide
CODEX_HOME ?= $(HOME)/.codex

.PHONY: generate build validate guide release-check install-skill clean

generate:
	xcodegen generate

build:
	xcodebuild -quiet -project $(PROJECT) -scheme $(SCHEME) -destination 'generic/platform=iOS Simulator' -derivedDataPath $(DERIVED_DATA) build
	@echo "xcodebuild ok"

validate:
	node -e "JSON.parse(require('fs').readFileSync('Tools/asset_manifest.json','utf8')); console.log('manifest ok')"

guide:
	mkdir -p Build Docs/pdf
	pandoc Docs/guide.md --standalone --embed-resources --resource-path=Docs --css Docs/guide-style.css --metadata title="RealityKit Asset and Texture Pipeline Guide" -o Build/realitykit-pipeline-guide.html
	weasyprint Build/realitykit-pipeline-guide.html Build/realitykit-pipeline-guide.pdf
	cp Build/realitykit-pipeline-guide.pdf Docs/pdf/realitykit-pipeline-guide.pdf

release-check: generate validate build

install-skill:
	mkdir -p "$(CODEX_HOME)/skills/$(SKILL_NAME)"
	cp -R "Skills/$(SKILL_NAME)/." "$(CODEX_HOME)/skills/$(SKILL_NAME)/"
	@echo "installed $(SKILL_NAME) to $(CODEX_HOME)/skills/$(SKILL_NAME)"

clean:
	rm -rf Build/DerivedData
