import numpy as np
import math



if __name__ == "__main__":
    #### 신경망 파라미터 불러오기
    weights = []
    biaseds = []
    temp_bundle_list = []
    fpath = "kiwoom/paramst.txt"
    file = open(fpath, 'r', encoding='utf8')
    lines = file.readlines()
    temp_list = []
    count = 1
    last_count = 0
    # print(len(lines))
    for line in lines:  # line 0900 종목 코드 10개
        ls = line.split("\t")
        for item in ls:
            if (item == "\n"):
                continue
            # temp_list 첫번째 줄
            temp_list.append(item)
        temp_bundle_list.append(temp_list.copy())
        if (count == 514):
            weights.append(temp_bundle_list.copy())
            temp_bundle_list.clear()
        elif (count == 516):
            biaseds.append(temp_bundle_list.copy())
            temp_bundle_list.clear()
        elif (count == 517):
            weights.append(temp_bundle_list.copy())
            temp_bundle_list.clear()
        elif (count == 518):
            biaseds.append(temp_bundle_list.copy())
            temp_bundle_list.clear()
        if (count % 64 == 0) and ((count / 64) % 2 == 1): # layer weight
            weights.append(temp_bundle_list.copy())
            temp_bundle_list.clear()
        elif (count % 64 == 0) and ((count / 64) % 2 == 0): # layer biased
            biaseds.append(temp_bundle_list.copy())
            temp_bundle_list.clear()
        temp_list.clear()
        count = count + 1
    # temp_input_data.reshape(1, 26)
    temp_input_data = [0.139922, 0.388440, 0.243455, 1.000000, 0.777279, 0.211327, 0.268225, 0.619771, 0.104559, 0.452556, 0.003096,
                       0.090696, 0.048931, 0.182139, 0.038477, 0.041504, 0.079789, 0.193202, 0.251944, 0.110299, 0.801724, 0.198276,
                       1.800000, 3.600000, -0.800000, -0.600000]
    print(weights)
    print(biaseds)
    #weights[0] = np.array(weights[0], dtype=np.float64)
    #biaseds[0] = np.array(biaseds[0], dtype=np.float64)

    # result1 = np.dot(temp_input_data, weights[0]) + biaseds[0]
    # print(result1.shape)
    # print(result1)
    #
    # result1tan = np.tanh(result1)
    #
    # print(result1tan.shape)
    # print(result1tan)

    #fast = np.tanh(np.dot(temp_input_data, weights[0]) + biaseds[0])
    # print(fast.shape)
    # print(fast)

    for i in range(len(weights)): # 0 ~ 8
        temp_weight = np.array(weights[i], dtype=np.float64)
        temp_biased = np.array(biaseds[i], dtype=np.float64)
        temp_input_data = np.tanh(np.dot(temp_input_data, temp_weight) + temp_biased)
    print(temp_input_data)
    file.close()



