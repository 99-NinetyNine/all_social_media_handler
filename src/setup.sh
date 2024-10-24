python3 -m venv venv
source venv/bin/activate
pip install "kivy[base,media]"

# mkdir kivy-deps-build && cd kivy-deps-build
# curl https://raw.githubusercontent.com/kivy/kivy/master/tools/build_linux_dependencies.sh -o build_kivy_deps.sh
# chmod +x build_kivy_deps.sh
# ./build_kivy_deps.sh
# export KIVY_DEPS_ROOT=$(pwd)/kivy-dependencies
