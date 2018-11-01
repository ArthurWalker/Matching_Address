import sys
import re
import csv


def processing_file(filename):
    count = 0
    with open(filename, 'r') as fin, open('small_example.csv', 'w') as fout:
        csv_reader = csv.reader(fin, delimiter=',')
        csv_writer = csv.writer(
            fout, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
        for line in csv_reader:
            #if (count == 100000):
             #   break
            if (count != 0):
                address_county = ' '.join(line[3:16])
                address_no_county = ' '.join(line[3:15])
                address_county = re.sub(r'NULL ', '', address_county)
                address_county = re.sub(r' NULL', '', address_county)
                address_no_county = re.sub(r'NULL ', '', address_no_county)
                address_no_county = re.sub(r' NULL', '', address_no_county)
                if (line[15] == 'NULL' and 'DUBLIN' in line[14]):
                    address_county += ' DUBLIN'
                if (re.search(r'[0-9]+\/[0-9]+', address_county)):
                    word = re.findall(r"[0-9]+\/[0-9]+", address_county)
                    new_word = re.sub("/", " ", word[0])
                    range_address_county = re.sub(word[0], new_word, address_county)
                    line = line+[address_no_county]+[address_county]+[range_address_county]
                elif (re.search(r'[0-9]+-[0-9]+', address_county)):
                    word = re.findall(r"[0-9]+-[0-9]+", address_county)
                    list_num = re.split("-", word[0])
                    list_range_num = [str(num) for num in range(
                        int(list_num[0]), int(list_num[1])+1)]
                    range_num = " ".join(list_range_num)
                    range_address_county = re.sub(word[0], range_num, address_county)
                    line = line+[address_no_county]+[address_county]+[range_address_county]
                elif (re.search(r'[0-9]+_[0-9]+', address_county)):
                    word = re.findall(r"[0-9]+_[0-9]+", address_county)
                    list_num = re.split("_", word[0])
                    list_range_num = [str(num) for num in range(
                        int(list_num[0]), int(list_num[1])+1,2)]
                    range_num = " ".join(list_range_num)
                    range_address_county = re.sub(word[0], range_num, address_county)
                    line = line+[address_no_county]+[address_county]+[range_address_county]
                else:
                    line = line+[address_no_county]+[address_county]
            csv_writer.writerow(line)
            count += 1
        else:
            print 'Done !'


def main():
    processing_file('../../Docs/GeoDirectoryData.csv')


if __name__ == '__main__':
    main()
