from starlette.applications import Starlette
from starlette.responses import UJSONResponse
import gpt_2_simple as gpt2
import tensorflow as tf
import uvicorn
import os
import gc


app = Starlette(debug=False)

sess = gpt2.start_tf_sess(threads=1)

response_header = {
    'Access-Control-Allow-Origin': '*'
}


@app.route('/', methods=['GET', 'POST', 'HEAD'])
async def homepage(request):
    global generate_count
    global sess

    if request.method == 'GET':
        params = request.query_params
    elif request.method == 'POST':
        params = await request.json()
    elif request.method == 'HEAD':
        return UJSONResponse({'text': ''},
                             headers=response_header)
    
    gpt2.load_gpt2(sess, run_name=params.get('run_name', ''))

    text = gpt2.generate(sess,
                         run_name=params.get('run_name', ''),
                         length=int(params.get('length', 1023)),
                         temperature=float(params.get('temperature', 0.7)),
                         top_k=int(params.get('top_k', 0)),
                         top_p=float(params.get('top_p', 0)),
                         prefix=params.get('prefix', '')[:500],
                         truncate=params.get('truncate', None),
                         include_prefix=str(params.get('include_prefix', True)).lower() == 'true',
                         return_as_list=True)[0]

    sess = gpt2.reset_session(sess)

    gc.collect()
    return UJSONResponse({'text': text},
                         headers=response_header)


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
