import os
import re
import timeit


def main():
    start = timeit.default_timer()
    store()
    end = timeit.default_timer()
    store_time = end - start
    start = timeit.default_timer()
    output = find()
    end = timeit.default_timer()
    find_time = end - start
    with open("../out/log.txt", "w") as log_obj:
        log_obj.writelines(output)
        log_obj.write(str(store_time*1000)+"\n")
        log_obj.write(str(find_time*1000)+"\n")

    pass


def find():
    with open("../out/sort.dat", "rb") as sort_obj, open("../in/test.txt", "r") as test_obj:
        outputs = []
        for word in test_obj:
            output = find_one(sort_obj, word.strip())
            if output is not None:
                outputs.append(output)
        return outputs


def find_one(sort_obj, word):
    size = os.fstat(sort_obj.fileno()).st_size
    block_num = int(size / 1024)
    output_next = False
    for block_index in range(0, block_num):
        block_local_index = 0
        sort_obj.seek(block_index * 1024)
        while block_local_index < 1024:
            t_len = sort_obj.read(1)
            if t_len == 0:
                break
            t = sort_obj.read(int.from_bytes(t_len, byteorder='big'))
            t_str = t.decode("utf-8")
            if output_next:
                return t_str + "\n"
            if word == t_str:
                output_next = True

            block_local_index = block_local_index + 1 + int.from_bytes(t_len, byteorder='big')

    return None


def store():
    words = set()
    with open("../in/sample.txt", "r") as sample_obj:
        for line in sample_obj:
            b = re.split(r'[^a-zA-Z_\']+', line)
            words |= set([w for w in b if len(w) > 0])
    words = list(words)
    words = sorted(words, key=str.lower)
    print(words)
    index = 0
    block_index = 0
    block = bytearray(1024)
    with open("../out/sort.dat", "wb") as sort_obj:
        while index < len(words):
            w = words[index]
            w_bytes = bytes(w, "utf-8")
            w_bytes_len = len(w_bytes)
            if w_bytes_len > 256:
                continue
            if block_index + 1 + w_bytes_len > 1024:
                sort_obj.write(block)
                block = bytearray(1024)
                block_index = 0
                pass
            else:
                block[block_index] = w_bytes_len
                block[block_index + 1:block_index + 1 + w_bytes_len] = w_bytes
                block_index = block_index + 1 + w_bytes_len
                index += 1
        if block_index != 0:
            sort_obj.write(block)


if __name__ == '__main__':
    main()
