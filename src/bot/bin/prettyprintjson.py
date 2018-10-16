#!/usr/bin/python3

import sys, getopt, simplejson, json

def main(argv):
   inputfile = ''
   outputfile = ''
   try:
      opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
   except getopt.GetoptError:
      print ('prettyprintjson.py -i <inputfile> -o <outputfile>')
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print ('prettyprintjson.py -i <inputfile> -o <outputfile>')
         sys.exit()
      elif opt in ("-i", "--ifile"):
         inputfile = arg
      elif opt in ("-o", "--ofile"):
         outputfile = arg
   print ('Input file is "', inputfile)
   print ('Output file is "', outputfile)
   with open(inputfile) as json_data:
       d = json.load(json_data)
       json_data.close()
       # now write output to a file
       out = open(outputfile, "w")
       # magic happens here to make it pretty-printed
       out.write(simplejson.dumps(d, indent=4, sort_keys=True))
       out.close()

if __name__ == "__main__":
   main(sys.argv[1:])
