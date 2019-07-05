


if(DEFINED POLLY_FLAGS_SANITIZE_UNDEFINED_CMAKE_)
    return()
else()
    set(POLLY_FLAGS_SANITIZE_UNDEFINED_CMAKE_ 1)
endif()

include(polly_add_cache_flag)

polly_add_cache_flag(CMAKE_CXX_FLAGS "-fno-omit-frame-pointer")
polly_add_cache_flag(CMAKE_CXX_FLAGS "-fsanitize=undefined")
polly_add_cache_flag(CMAKE_CXX_FLAGS "-fsanitize=implicit-integer-truncation")
polly_add_cache_flag(CMAKE_CXX_FLAGS "-fsanitize=implicit-integer-arithmetic-value-change")
polly_add_cache_flag(CMAKE_CXX_FLAGS "-fsanitize=implicit-conversion")
polly_add_cache_flag(CMAKE_CXX_FLAGS "-fsanitize=integer")
polly_add_cache_flag(CMAKE_CXX_FLAGS "-fsanitize=nullability")
polly_add_cache_flag(CMAKE_CXX_FLAGS "-g")

polly_add_cache_flag(CMAKE_C_FLAGS "-fno-omit-frame-pointer")
polly_add_cache_flag(CMAKE_C_FLAGS "-fsanitize=undefined")
polly_add_cache_flag(CMAKE_C_FLAGS "-fsanitize=implicit-integer-truncation")
polly_add_cache_flag(CMAKE_C_FLAGS "-fsanitize=implicit-integer-arithmetic-value-change")
polly_add_cache_flag(CMAKE_C_FLAGS "-fsanitize=implicit-conversion")
polly_add_cache_flag(CMAKE_C_FLAGS "-fsanitize=integer")
polly_add_cache_flag(CMAKE_C_FLAGS "-fsanitize=nullability")
polly_add_cache_flag(CMAKE_C_FLAGS "-fsanitize-memory-track-origins")

polly_add_cache_flag(CMAKE_C_FLAGS "-g")