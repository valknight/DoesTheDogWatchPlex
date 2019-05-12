
python build_json.py
 
if [ $? -eq 0 ]
then
  python write_to_plex.py
else
  exit 1
fi