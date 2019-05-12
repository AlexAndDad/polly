


if(DEFINED POLLY_FLAGS_FSTANDALONE_DEBUG_CMAKE_)
    return()
else()
    set(POLLY_FLAGS_FSTANDALONE_DEBUG_CMAKE_ 1)
endif()


include(polly_add_cache_flag)

polly_add_cache_flag(CMAKE_CXX_FLAGS "-fstandalone-debug")