#define PY_SSIZE_T_CLEAN size_t
#include <Python.h>
#include <stdlib.h>
#include "zopfli.h"
#include "deflate.h"
#include "util.h"

static PyObject *
zopfli_deflate(PyObject *self, PyObject *args, PyObject *keywrds)
{
  const unsigned char *in, *out;
  unsigned char *in2, *out2;
  size_t insize=0;
  size_t prehist=0; 
  size_t outsize=0;  
  ZopfliOptions options;
  ZopfliInitOptions(&options);
  options.verbose = 0;
  options.numiterations = 15;
  options.blocksplitting = 1;
  options.blocksplittinglast = 0;
  options.blocksplittingmax = 15;
  int blocktype = 2;
  int blockfinal = 1;
  unsigned char bitpointer = 0;
  
  static char *kwlist[] = {"data", "verbose", "numiterations", "blocksplitting", "blocksplittinglast", "blocksplittingmax", "blocktype","blockfinal","bitpointer","old_tail","prehist", NULL};
  
  if (!PyArg_ParseTupleAndKeywords(args, keywrds, "s#|iiiiiiiBs#i", kwlist, &in, &insize,
				   &options.verbose,
				   &options.numiterations,
				   &options.blocksplitting,
				   &options.blocksplittinglast,
				   &options.blocksplittingmax,
				   &blocktype,
				   &blockfinal,
				   &bitpointer,
				   &out, &outsize,
				   &prehist))
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  in2 = malloc(insize);
  memcpy(in2, in, insize);
  out2 = malloc(outsize);
  memcpy(out2, out, outsize);
  
  ZopfliDeflatePart(&options, blocktype, blockfinal, in2, prehist, insize, &bitpointer, &out2, &outsize);
  
  free(in2);
  Py_END_ALLOW_THREADS
  PyObject *returnValue;
  returnValue = Py_BuildValue("s#B", out2, outsize, bitpointer);
  free(out2);
  return returnValue;
}

static char docstringd[] = "" 
  "zopfli.zopfli.compress applies zopfli deflate compression to an obj." 
  "" \
  "zopfli.zopfli.compress("
  "  s, **kwargs, verbose=0, numiterations=15, blocksplitting=1, "
  "  blocksplittinglast=0, blocksplittingmax=15, "
  "  blocktype=2, blockfinal=1, bitpointer=0, oldtail='', prehist=0)"
  "";


static PyObject *ZopfliError;

static PyMethodDef ZopfliMethods[] = {
  { "deflate", zopfli_deflate,  METH_KEYWORDS, docstringd},

  { NULL, NULL, 0, NULL}
};


PyMODINIT_FUNC
initzopfli(void)
{
  PyObject *m;

  m = Py_InitModule("zopfli", ZopfliMethods);
  if (m == NULL) 
    return;

  ZopfliError = PyErr_NewException("zopfli.error", NULL, NULL);
  Py_INCREF(ZopfliError);
  PyModule_AddObject(m, "error", ZopfliError);
}

