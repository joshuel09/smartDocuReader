from __future__ import print_function
from django.shortcuts import render
import markdown
from django.http import HttpResponseRedirect
from .models import Document
from llama_index import GPTVectorStoreIndex, SimpleDirectoryReader, LLMPredictor
from llama_index import download_loader, StorageContext, load_index_from_storage
from langchain import OpenAI
from django.http import HttpResponse

CJKPDFReader = download_loader("CJKPDFReader")
loader = CJKPDFReader()

def home(request):
    return render(request, 'upload.html')

def upload_document(request):
    if request.method == 'POST':
        document = Document(file=request.FILES['document'])
        document.save()

        # Get the uploaded file path
        file_path = document.file.path

        # Load the index from the uploaded file
        index = GPTVectorStoreIndex.from_documents(loader.load_data(file_path))

        # Persist the index
        index.storage_context.persist(persist_dir="index")

        return HttpResponseRedirect('/process')

    return render(request, 'upload.html')

def process_document(request):
    document = Document.objects.last()  # Get the latest uploaded document
    if request.method == 'POST':

        query_text = request.POST['question']
        query_format = "please convert the text as markdown"

        llm_predictor = LLMPredictor(llm=OpenAI(temperature=0, max_tokens=350))
        # rebuild storage context
        storage_context = StorageContext.from_defaults(persist_dir="index")

        # load index
        index = load_index_from_storage(storage_context)
        query_engine = index.as_query_engine(llm_predictor=llm_predictor)
        response = query_engine.query(query_text + query_format)

        return render(request, 'process.html', {'response':  markdown.markdown(str(response)), 'uploaded_file': document.file.name, 'question': query_text})

    return render(request, 'process.html', {'uploaded_file': document.file.name})

