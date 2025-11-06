from pybtex.database.input import bibtex
import os
parser = bibtex.Parser()
bib_data = parser.parse_file('pubs.bib')

year_rev_sort=[]
for k in bib_data.entries.keys():
    if "year" not in bib_data.entries[k].fields:
        print("Publication "+str(k)+" has no year!")
        exit()    
    year_rev_sort.append((k,int(bib_data.entries[k].fields["year"])))


#year_rev_sort=[e[0] for e in reversed(sorted(year_rev_sort,key=lambda f: f[1]))]
year_rev_sort=[e[0] for e in year_rev_sort] # Manual sort

def format_name(p):    
    midnames=[mn+("." if len(mn)==1 else "") for mn in p.middle_names ]
    return " ".join(p.first_names)+" "+" ".join(midnames)+(" " if len(midnames)>0 else "")+" ".join(p.prelast_names)+(" " if len(p.prelast_names)>0 else "")+ " ".join(p.last_names)

abbrevs={}
abbrevs["europhysics letters"]="EPL"
abbrevs["the european physical journal b"]="Eur. Phys. J. B"
abbrevs["proceedings of the national academy of sciences"]="PNAS"
abbrevs["journal of colloid and interface science"]="J. Colloid Interface Sci."
abbrevs["journal of computational physics"]="J. Comp. Phys."
abbrevs["journal of fluid mechanics"]="J. Fluid Mech."
abbrevs["physical review letters"]="Phys. Rev. Lett."
abbrevs["physical review fluids"]="Phys. Rev. Fluids"
abbrevs["computer methods in applied mechanics and engineering"]="Comput. Methods Appl. Mech. Eng."
abbrevs["physical review applied"]="Phys. Rev. Appl."
abbrevs["communications in computational physics"]="Commun. Comput. Phys."
abbrevs["advanced science"]="Adv. Sci."
def format_journal(e):
    
    
    if e.type=="incollection":
        res="In: <I>"+e.fields["booktitle"].lstrip("{").rstrip("}")+"</I>"  
        res+=", "+e.fields["publisher"]+", ("+e.fields["year"]+")."
    else:
        res=e.fields["journal"]
        if res.lower() in abbrevs or ():
            res=abbrevs[res.lower()]
        if res.startswith("arXiv"):
            res="<I>submitted</I>."
        else:
            res="<I>"+res+"</I>"
            if "volume" not in e.fields:
                raise RuntimeError("MISSING VOLUME "+str(e))            
            res+=" "+"<B>"+e.fields["volume"]+"</B>"
            if "pages" not in e.fields:
                raise RuntimeError("MISSING PAGES "+str(e))            
            res+=", "+str(e.fields["pages"].replace("--","&ndash;").replace("-","&ndash;"))
            res+=", ("+str(e.fields["year"])+")."
    return res

def format_author_list(al):
    res=""
    for i,p in enumerate(al):
        res=res+format_name(p)
        if i<len(al)-2:
            res=res+", "
        elif i<len(al)-1:
            res=res+" & "
    return res

print("<ol>")
cnt=len(year_rev_sort)
for entry_name in year_rev_sort:
    entry=bib_data.entries[entry_name]       
    print('<li value="'+str(cnt)+'">')

    
    print(format_author_list(entry.persons["author"])+", ")

    url=None
    if "doi" in entry.fields:
        url="https://dx.doi.org/"+entry.fields["doi"].lstrip("https://").lstrip("doi.org/").lstrip("dx.doi.org/")
    elif "url" in entry.fields:
        url=entry.fields["url"]
    if url is not None:    
        print('<A href="'+url+'""><i>')
    print(entry.fields["title"].lstrip("{").rstrip("}"))
    if url is not None:
        print("</i></A>")
    print("</i>, ")
        
    print(format_journal(entry))
    pdflink="pdf/"+entry_name+".pdf"
    
    pdftype="preprint"
    if "eprint" in entry.fields:
        pdflink=entry.fields["eprint"]
        if pdflink.find("arxiv.org")>-1:
            pdftype="arXiv preprint"
        else:
            pdftype="Open Access"
    elif not os.path.exists(pdflink):
        pdflink=None
    if pdflink is not None:
        print('<A href="'+pdflink+'" target="_blank">[PDF ('+pdftype+')]</A>')
    cnt=cnt-1
    
print("</ol>")
