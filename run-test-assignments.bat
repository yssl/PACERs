pacers.py test-assignments\c-1
pacers.py test-assignments\c-2 --user-input "1 2" "3 4"

pacers.py --interpreter-cmd "py -2" test-assignments\python2
pacers.py --interpreter-cmd "py -3" test-assignments\python3

pacers.py test-assignments\txt

pacers.py test-assignments\img

pacers.py test-assignments\zip-1 --user-input "2 5" "10 20"
pacers.py test-assignments\zip-2 --user-input "2 5" "10 20"

pacers.py test-assignments\dir --user-input "2 5" "10 20"

pacers.py test-assignments\cmake

pacers.py test-assignments\vcxproj

pacers.py test-assignments\vcxproj-GUI --build-only --exclude-patterns SDL2-2.0.4/*
pacers.py test-assignments\vcxproj-GUI --run-only-serial --timeout 0 --exclude-patterns SDL2-2.0.4/*
