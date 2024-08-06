def longest_common_substring(str1: str, str2: str) -> str:
    # 获取两个字符串的长度
    len1, len2 = len(str1), len(str2)

    # 初始化一个二维数组，用于保存动态规划的状态
    dp = [[0] * (len2 + 1) for _ in range(len1 + 1)]
    longest_length = 0
    longest_end_pos = 0

    # 填充动态规划表
    for i in range(1, len1 + 1):
        for j in range(1, len2 + 1):
            if str1[i - 1] == str2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
                if dp[i][j] > longest_length:
                    longest_length = dp[i][j]
                    longest_end_pos = i
            else:
                dp[i][j] = 0

    # 提取最长公共子串
    longest_common_substring = str1[longest_end_pos - longest_length: longest_end_pos]
    return longest_common_substring
