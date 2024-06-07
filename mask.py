import cpca
from pyhanlp import HanLP
import pandas as pd
import os

### 去除号码
def remove_spaces(string: str):
    # 使用 replace() 函数将所有空格替换为空字符串
    try:
        result = string.replace(" ", "")
        result = string.replace("-", "")
        result = string.replace("_", "")
        return result
    except Exception as e:
        print("Remove Space Error: %s" % e)
        return string
        

def mask_numbers_in_text(string: str):
    string_nospace = remove_spaces(string)
    pos_list = [i for i in range(len(string_nospace)) if str.isdigit(string_nospace[i])]
    if len(pos_list) == 0:
        return string
    pos_info = []
    count = 1
    start = pos_list[0]
    # 寻找连续数字
    for i in range(1, len(pos_list)):
        if pos_list[i] - pos_list[i-1] == 1:
            count += 1
            continue
        else:
            end = pos_list[i-1]
            if start != end:
                resp = {"start": start, "len": count}
                pos_info.append(resp)
                count = 1
            start = pos_list[i]
    end = pos_list[-1]
    if start != end:
        resp = {"start": start, "len": count}
        pos_info.append(resp)
    # print(pos_info)
    # 抹掉长数字
    for item in pos_info:
        if item["len"] < 7:
            # print(f"skipped: {item}")
            continue
        mask = "*" * item["len"]
        start = item["start"]
        end = item["start"] + item["len"]
        # print(start, end)
        string_nospace = string_nospace[:start] + mask + string_nospace[end:]
    return string_nospace

### 去除邮箱
def is_valid_email(email):
    if "@" in email and "." in email.split("@")[1]:
        at_index = email.index("@")
        dot_index = email.index(".", at_index)
        if at_index < dot_index and at_index != 0:
            return True
    return False

def mask_email(email):
    at_index = email.index("@")
    local_part = email[:at_index]
    domain_part = email[at_index+1:]
    
    # Mask the local part except the first and last character
    masked_local_part = local_part[0] + "****"
    
    # Mask the domain part except the first character and the top-level domain
    domain_name, tld = domain_part.rsplit(".", 1)
    masked_domain_part = "****" + "." + tld
    
    masked_email = masked_local_part + "@" + masked_domain_part
    return masked_email

def mask_emails_in_text(text):
    words = text.split()
    masked_words = []
    for word in words:
        if is_valid_email(word):
            masked_words.append(mask_email(word))
        else:
            masked_words.append(word)
    return " ".join(masked_words)

### 去除地址
def mask_addr_in_text(string: str):
    str_list = [string]
    loc_df = cpca.transform(str_list)

    for col in loc_df.columns:
        value = loc_df.at[0, col]
        if str(value) in string:
            if col == '省':
                string = string.replace(value, '**省')
            elif col == '市':
                string = string.replace(value, '**市')
            elif col == '区':
                string = string.replace(value, '**区')
            else:
                string = string.replace(value, '*****')
    return string

### 去除名字
def mask_name_in_text(sentences: str):
    segment = HanLP.newSegment().enableNameRecognize(True)
    seg_words = segment.seg(sentences)
    result = sentences
    for value in seg_words:
        split_words = str(value).split('/')  # check //m
        word, tag = split_words[0], split_words[-1]
        if tag == 'nr':
            result = result.replace(word, '***')    
    return result

if __name__ == "__main__":
    DATA_DIR = "data"
    OUTPUT_DIR = "data_masked"

    excel_files = os.listdir(DATA_DIR)
    csv_files = os.listdir(OUTPUT_DIR)
    for f in excel_files:
        if '$' in f:
            continue
        df = pd.read_excel(os.path.join(DATA_DIR, f))
        masked_msgs = []
        for index, row in df.iterrows():
            print(index)
            if row['谁说'] != "客户":
                continue
            msg = row['消息正文']
            print(msg)
            if not isinstance(msg, str):
                msg = str(msg)
                print("msg not str")
            # 手机号邮箱打码处理
            masked = mask_numbers_in_text(msg)
            masked = mask_emails_in_text(masked)
            masked = mask_addr_in_text(masked)
            masked = mask_name_in_text(masked)
            if "***" in masked and "***" not in msg:
                df.at[index, '消息正文'] = masked
                print("masked: %s" % masked)

        df.to_csv(os.path.join(OUTPUT_DIR, f.split(".xlsx")[0] + ".csv"), index=False, encoding="utf_8_sig")
        print(f"############### 完成处理：{f} ###############")
        
    print("DONE")