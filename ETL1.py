#ETL Microdados do INEP = Educação Superior
#Autor: Escobar
#Data: 14/08/2023

#Conectar na base do DW_INEP
import mysql.connector
import pandas as pd

#Dictionary com a config do banco para conexão
config = {
    'user':'root',
    'password':'1234',
    'host': 'localhost',
    'database':'dw_inep',
    'port': '3306'
}
try:
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()

    # dados = pd.read_csv('C:/Users/Aluno/Downloads/Microdados do Censo da Educação Superior 2020/dados/MICRODADOS_CADASTRO_CURSOS_2020.CSV',sep=';', encoding='iso-8859-1')
    dados = pd.read_csv('C:/Users/Kaique.Fernandes/Documents/GitHub/DataScience/Etl_Atv1/microdados_censo_da_educacao_superior_2020/dados/MICRODADOS_CADASTRO_CURSOS_2020.CSV'
                        ,sep=';'
                        , encoding='iso-8859-1'
                        , low_memory=False)
    dados = dados.fillna('')    
    #UF
    dados_uf = pd.DataFrame(dados['NO_UF'].unique(), columns = ['uf'])
    

    for i, r in dados_uf.iterrows():
        insert_statement = 'insert into dim_uf (tf_uf, uf) values (' \
                            + str(i) +',\'' \
                            + str(r['uf']) +'\')'
        print(insert_statement)
        cursor.execute(insert_statement)
        conn.commit()
    
    #Municipio
    dados_municipio = pd.DataFrame(dados['NO_MUNICIPIO'].unique(), columns = ['Municipio'])

    for i,r in dados_municipio.iterrows():
        municipio = r['Municipio']
        municipio = municipio.replace("'","")
        insert_statement = f"insert into dim_municipio (tf_municipio, municipio) values({i}, '{municipio}')"
        print(insert_statement)
        cursor.execute(insert_statement)
        conn.commit()

    #modalidade ensino
    dados_modalidade = pd.DataFrame(dados['TP_MODALIDADE_ENSINO'].unique(), columns = ['tp_modalidade_ensino'])
    for i,r in dados_modalidade.iterrows():
        if r['tp_modalidade_ensino'] == 1:
            insert_statement = f"insert into dim_modalidade (tf_modalidade, modalidade) values({r['tp_modalidade_ensino']}, 'Presencial')"
        elif  r['tp_modalidade_ensino'] == 2:
            insert_statement = f"insert into dim_modalidade (tf_modalidade, modalidade) values({r['tp_modalidade_ensino']}, 'EAD')"

      
        cursor.execute(insert_statement)
        conn.commit()

    #CURSO
    dados_curso = pd.DataFrame(dados['NO_CURSO'].unique(), columns = ['curso'])
    for i,r in dados_curso.iterrows():
        insert_statement = f"insert into dim_curso (tf_curso, curso) values({i+1}, '{r['curso']}')"
        cursor.execute(insert_statement)
        conn.commit()
    
    #ano
    dados_ano= pd.DataFrame(dados['NU_ANO_CENSO'].unique(), columns = ['ano'])
    for i,r in dados_ano.iterrows():
        insert_statement = f"insert into dim_ano (tf_ano, ano) values({i+1}, '{r['ano']}')"
        cursor.execute(insert_statement)
        conn.commit()
    

    
    # #ies
    dados_IES = pd.read_csv('C:/Users/Kaique.Fernandes/Documents/GitHub/DataScience/Etl_Atv1/microdados_censo_da_educacao_superior_2020/dados/MICRODADOS_CADASTRO_IES_2020.CSV'
                    ,sep=';'
                    , encoding='iso-8859-1'
                    , low_memory=False)
    dados_IES = dados_IES[['CO_IES','NO_IES']]
    

    dados_IES_curso = pd.DataFrame(dados['CO_IES'].unique(), columns = ['co_ies'])
    for i, r in dados_IES_curso.iterrows():
        #determinar o nome  da ies
        dados_IES_filtrado=dados_IES[dados_IES['CO_IES'] == r['co_ies']]
        no_ies = dados_IES_filtrado['NO_IES'].iloc[0].replace("'","")
        insert_statement = f"insert into dim_ies (tf_ies, ies) values({i+1}, '{no_ies}')"
        cursor.execute(insert_statement)
        conn.commit()

    #Fact matriculas
    for i, r in dados.iterrows():
        if r['TP_MODALIDADE_ENSINO'] == 1:
            modalidade  = 'Presencial'
        elif  r['TP_MODALIDADE_ENSINO'] == 2:
            modalidade = 'EAD'

        tf_uf_select_statement= f"select tf_uf from dim_uf where uf ='{r['NO_UF']}'" if r['NO_UF'] else "select Null from dim_uf"
        tf_municipio_select_statement= f"select tf_municipio from dim_municipio where municipio = '{r['NO_MUNICIPIO']}'" if r['NO_MUNICIPIO'] else "select Null from dim_municipio"

        dados_IES_filtrado=dados_IES[dados_IES['CO_IES'] == r['CO_IES']]
        no_ies = dados_IES_filtrado['NO_IES'].iloc[0].replace("'","")

        insert_statement = f"""insert into fact_matriculas(matriculas,tf_ano,tf_curso,tf_ies,tf_uf,tf_municipio,tf_modalidade)
        select distinct * from 
        (select {r['QT_INSCRITO_TOTAL']}) as matriculas,
        (select tf_ano from dim_ano where ano = {r['NU_ANO_CENSO']}) as tf_ano,
        (select tf_curso from dim_curso where curso = '{r['NO_CURSO']}') as tf_curso,
        (select tf_ies from dim_ies where ies = '{no_ies}') as tf_ies,
        ({tf_uf_select_statement}) as tf_uf,
        ({tf_municipio_select_statement}) as tf_municipio,
        (select tf_modalidade from dim_modalidade where modalidade = '{modalidade}') as tf_modalidade
        """
        print(insert_statement)
        cursor.execute(insert_statement)
        conn.commit()
    print('Acabou!')
#Necessári refatorar para corrigir a parte da IES e da modalidade
#Há nomesde atributos com erro. Necessário corrigir



except Exception as e:
    print(e)

