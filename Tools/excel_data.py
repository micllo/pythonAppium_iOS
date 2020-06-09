# -*- coding:utf-8 -*-
import xlrd, os


# 读取excel操作，所有数据存放在字典中
def read_excel(filename, index):
    xls = xlrd.open_workbook(filename)
    sheet = xls.sheet_by_index(index)
    # print(sheet.nrows)
    # print(sheet.ncols)
    dic = {}
    for j in range(sheet.ncols):
        data = []
        for i in range(sheet.nrows):
            data.append(sheet.row_values(i)[j])
        dic[j] = data
    return dic


if __name__ == '__main__':
    current_path = os.path.split(os.path.realpath(__file__))[0].split('C')[0]
    data = read_excel(current_path + "Data/testdata.xlsx", 0)
    print(data)
    print(data.get(1)[2])
    print(type(data.get(1)[2]))

