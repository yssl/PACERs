REM Programming languages
pacers.py test-assignments\c --std-input "1 2" "3 4"

pacers.py --interpreter-cmd "py -2" test-assignments\python2
pacers.py --interpreter-cmd "py -3" test-assignments\python3

REM Program inputs
pacers.py test-assignments\stdin-cmdarg-1 --std-input "2 1" --cmd-args "a b \"cd ef\""
pacers.py test-assignments\stdin-cmdarg-2 --std-input "2 1" "2 2" "2 3" --cmd-args "a b" "c d" "e f"
pacers.py test-assignments\stdin-cmdarg-3 --std-input "2 1" "2 2" "2 3" --cmd-args "a b"
pacers.py test-assignments\stdin-cmdarg-4 --cmd-args "a b" "c d"
pacers.py test-assignments\stdin-cmdarg-5 --std-input "2 1" "2 2" "2 3"

REM Projects
pacers.py test-assignments\cmake

pacers.py test-assignments\vcxproj
pacers.py test-assignments\vcxproj-GUI --build-only --exclude-patterns SDL2-2.0.4/*
pacers.py test-assignments\vcxproj-GUI --run-only-serial --timeout 0 --exclude-patterns SDL2-2.0.4/*

REM Text and image files
pacers.py test-assignments\txt
pacers.py test-assignments\img

REM SOURCE_FILES submission type
pacers.py test-assignments\source_files-zip-1 --std-input "2 5" "10 20"
pacers.py test-assignments\source_files-zip-2 --std-input "2 5" "10 20"
pacers.py test-assignments\source_files-dir --std-input "2 5" "10 20"

REM Error cases
pacers.py test-assignments\error-cases
