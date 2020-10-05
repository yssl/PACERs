pacers.py test-assignments\c-1
pacers.py test-assignments\c-2 --std-input "1 2" "3 4"

pacers.py test-assignments\stdin-cmdarg-1 --std-input "2 1" --cmd-args "a b \"cd ef\""
pacers.py test-assignments\stdin-cmdarg-2 --std-input "2 1" "2 2" "2 3" --cmd-args "a b" "c d" "e f"
pacers.py test-assignments\stdin-cmdarg-3 --std-input "2 1" "2 2" "2 3" --cmd-args "a b"
pacers.py test-assignments\stdin-cmdarg-4 --cmd-args "a b" "c d"
pacers.py test-assignments\stdin-cmdarg-5 --std-input "2 1" "2 2" "2 3"

pacers.py --interpreter-cmd "py -2" test-assignments\python2
pacers.py --interpreter-cmd "py -3" test-assignments\python3

pacers.py test-assignments\txt

pacers.py test-assignments\img

pacers.py test-assignments\zip-1 --std-input "2 5" "10 20"
pacers.py test-assignments\zip-2 --std-input "2 5" "10 20"

pacers.py test-assignments\dir --std-input "2 5" "10 20"

pacers.py test-assignments\cmake

pacers.py test-assignments\vcxproj

pacers.py test-assignments\vcxproj-GUI --build-only --exclude-patterns SDL2-2.0.4/*
pacers.py test-assignments\vcxproj-GUI --run-only-serial --timeout 0 --exclude-patterns SDL2-2.0.4/*
