import os, openpyxl, csv
dicUF = {'AC':'Acre', 'AL':'Alagoas', 'AM':'Amazonas', 'AP':'Amapá', 'BA':'Bahia', 'CE':'Ceará', 'DF':'Distrito Federal', 'ES':'Espírito Santo', 'GO':'Goiás', 'MA':'Maranhão', 'MT':'Mato Grosso', 'MS':'Mato Grosso do Sul', 'MG':'Minas Gerais', 'PA':'Pará', 'PB':'Paraíba', 'PR':'Paraná', 'PE':'Pernambuco', 'PI':'Piauí', 'RJ':'Rio de Janeiro', 'RN':'Rio Grande do Norte', 'RS':'Rio Grande do Sul', 'RO':'Rondônia', 'RR':'Roraima', 'SC':'Santa Catarina', 'SP':'São Paulo', 'SE':'Sergipe', 'TO':'Tocantins', 'TODOS':'Todos'}
raiz = "C:\\Users\\matheus\\Documents\\Checagem respostas tribunais\\Final\\2aRaspDecisoes\\CorrigiuCorreg\\ComTabelas"
dest = "C:\\Users\\matheus\\Documents\\Checagem respostas tribunais\\Final\\2aRaspDecisoes\\CorrigiuCorreg\\ComTabelas\\CSVs"

def formaCSVs(tribunal):
    xlFonte = openpyxl.load_workbook(os.path.join(raiz, "TRE-%s_SADP_TABELASv1.xlsx" % tribunal))
    for sheet in ('processos', 'partes_sadp', 'decisoes_finais'):
        fileCSV = open(os.path.join(dest, "TRE-%s_SADP_%s.csv" % (tribunal, sheet)), 'w', encoding='utf-8', newline='')
        writerCSV = csv.writer(fileCSV)
        for lin in range(1, xlFonte[sheet].max_row+1):
            linhaCSV = []
            for col in range(1, xlFonte[sheet].max_column+1):
                linhaCSV.append(xlFonte[sheet].cell(lin, col).value)
            writerCSV.writerow(linhaCSV)

if __name__ == '__main__':
    formaCSVs('DF')

