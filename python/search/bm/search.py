# -*- coding: utf-8 -*-
import os
import sys
import gc


# http://www.ruanyifeng.com/blog/2013/05/boyer-moore_string_search_algorithm.html

def boyer_moore_search(source_str, search_str):
    gc.disable()

    source_str_len = len(source_str)
    search_str_len = len(search_str)
    print 'source string length: %d, search string length: %d' \
        % (source_str_len, search_str_len)

    # 计算坏字符的位置，需要注意的细节：
    # 1. 最后一个字符不需计算，因为是倒退匹配的，如果搜索串最后一个是坏字符的话，
    # 2. 只计算最后一次出现
    bad_char = {}
    for index, char in enumerate(search_str[:search_str_len - 1]):
        bad_char[char] = index
    print 'bad char dict created, ', bad_char

    # 计算好后缀的位置
    # 这里计算两个值，一个是当它是最大后缀是的位置
    # 一个是当它不是最大后缀时，是否会在头部出现
    good_suffix = {}
    for i in range(search_str_len - 1, 0, -1):
        suffix = search_str[i:]
        pos1 = search_str[:i].rfind(suffix)
        if pos1 != -1:
            pos1 = pos1 + len(suffix) - 1
        pos2 = -1
        if search_str.startswith(suffix):
            pos2 = len(suffix) - 1
        good_suffix[suffix] = (pos1, pos2)
    print 'good suffix dict created, ', good_suffix

    # 第一步对齐，"字符串"与"搜索词"头部对齐，指针指向搜索词尾部
    source_str_ptr = search_str_ptr = search_str_len - 1

    # 后缀指针，指向当前发现的后缀
    suffix_ptr = 0
    suffix_stack = []

    while source_str_ptr < source_str_len:
        print source_str_ptr, search_str_ptr, suffix_ptr,
        start = source_str_ptr-search_str_len+1
        if start < 0: start = 0
        print '-------', source_str[start:source_str_ptr+search_str_len],
        print '-------', search_str[0:search_str_ptr+1]
        # 最后一个字符不相等，发现了 "坏字符"，需要向后跳
        if source_str[source_str_ptr] != search_str[search_str_ptr]:
            # 首先应用“坏字符规则”
            # 后移位数 = 坏字符的位置 - 搜索词中的上一次出现位置
            # bad_char_skip_steps = search_str_ptr - bad_char_last_pos
            bad_char_last_pos = bad_char.get(source_str[source_str_ptr], -1)
            #坏字符出现过，可能多次，最后一次在坏字符的位置的后面，
            # 保守处理：不回退原则，向后移一位
            # 激进处理：全部跳过
            if bad_char_last_pos > search_str_ptr:
                bad_char_last_pos = search_str_ptr - 1#-1
            bad_char_skip_steps = search_str_ptr - bad_char_last_pos
            print 'skip steps calculated by bad char rule is: %d' % bad_char_skip_steps

            # 其次应用“好后缀规则”
            # 如果suffix_ptr，那么已经发现了好后缀，并且这些后缀存放在suffix_stack中
            skipsteps = 0
            if suffix_ptr != 0:
                # 最长好后缀是否存在
                print 'there is suffix'
                suf = suffix_stack.pop()
                found = 0
                if suf in good_suffix and good_suffix[suf][0] != -1:
                    steps2 = good_suffix[su]
                    print 'find longest suffix.', suf
                    found = 1
                else:
                    while 1:
                        try:
                            s = suffix_stack.pop()
                            print 'caculate a suffix', s
                            steps2 = good_suffix[s][1]
                            if steps2 != -1 and steps2==(len(s)-1):
                                print 'find a suffix', s
                                found = 1
                        except: break
                if found == 1:
                    skipsteps = (search_str_len - 1 - steps2)
                    print 'skip steps by good suffix', search_str_ptr, skipsteps

            # 不存在，其余好后缀是否发生在头部

            steps = max(bad_char_skip_steps, skipsteps)
            print 'choose skip steps', steps
            source_str_ptr += steps
            source_str_ptr += suffix_ptr # 字符串到上次移动位置，去掉后缀影响
            # 发现了坏字符，将几个指针复原到对应位置
            search_str_ptr = search_str_len - 1 # 搜索词 复原
            suffix_ptr = 0 # 后缀复原

        else:
            suffix_ptr += 1
            #print "******", search_str[search_str_len - suffix_ptr:]
            suffix_stack.append(search_str[search_str_len - suffix_ptr:])
            # 后缀与搜索词相等，则已经发现
            if suffix_ptr == search_str_len:
                print 'found:', source_str_ptr, search_str_ptr, suffix_ptr
                break
            # 前移一位，进行比较
            source_str_ptr = source_str_ptr - 1
            search_str_ptr = search_str_ptr - 1
    gc.enable()

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print "USAGE: python %s search_string source_string/source_file_path [source_string/source_file_path]" % __file__

    search_str = sys.argv[1]

    for source in sys.argv[2:]:
        if not os.path.exists(source):
            boyer_moore_search(source, search_str)
        else:
            with open(source, "rb") as f:
                source_file = f.read()
                boyer_moore_search(source_file, search_str)






