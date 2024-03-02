#include <Python.h>
#include <iostream>

// init_python - configure interpreter details here
PyStatus init_python(const char *program_name)
{
    PyStatus status;

    PyConfig config;
    PyConfig_InitPythonConfig(&config);

    /* Set the program name before reading the configuration
       (decode byte string from the locale encoding).

       Implicitly preinitialize Python. */
    status = PyConfig_SetBytesString(&config, &config.program_name,
                                     program_name);
    if (PyStatus_Exception(status)) {
        goto done;
    }

    /* Read all configuration at once */
    status = PyConfig_Read(&config);
    if (PyStatus_Exception(status)) {
        goto done;
    }

    /* Specify sys.path explicitly */
    /* If you want to modify the default set of paths, finish
       initialization first and then use PySys_GetObject("path") */
    config.module_search_paths_set = 1;
    status = PyWideStringList_Append(&config.module_search_paths,
                                     L"./Python-3.11.1/Lib");
    if (PyStatus_Exception(status)) {
        goto done;
    }

    /* Add two entries to module paths: the compiled Python modules, and local files */
    status = PyWideStringList_Append(&config.module_search_paths,
                                     L"./Python-3.11.1/Modules");
    if (PyStatus_Exception(status)) {
        goto done;
    }
    status = PyWideStringList_Append(&config.module_search_paths,
                                     L"."); // may want to turn this into a "./scripts" subdirectory
    if (PyStatus_Exception(status)) {
        goto done;
    }

    /* Override executable computed by PyConfig_Read() */
    status = PyConfig_SetString(&config, &config.executable,
                                L".");
    if (PyStatus_Exception(status)) {
        goto done;
    }

    status = Py_InitializeFromConfig(&config);

done:
    PyConfig_Clear(&config);
    return status;
}


// C++ example functionality
int recurse_fib(int i)
{
    if (i <= 1) return 1;
    return recurse_fib(i-1) + recurse_fib(i-2);
}

// Create a python module to expose C++ functionality
static PyObject* scriptable_fibonacci(PyObject *self, PyObject *args)
{
    int x;
    // get input (single integer) from args
    if (!PyArg_ParseTuple(args, "i", &x)) return NULL;
    return PyLong_FromLong(recurse_fib(x));
}

static PyMethodDef scriptableMethods[] = {
    {"fibonacci", scriptable_fibonacci, METH_VARARGS,
        "Fibonacci sequence by index"},
    {NULL, NULL, 0, NULL}
};

static PyModuleDef scriptableModule = {
    PyModuleDef_HEAD_INIT, "scriptable", NULL, -1, scriptableMethods,
    NULL, NULL, NULL, NULL
};

static PyObject* PyInit_scriptable(void)
{
    return PyModule_Create(&scriptableModule);
}

int main()
{
    std::cout << "[C++] Initializing Python\n";
    //Express this program as a module before pyinit
    PyImport_AppendInittab("scriptable", &PyInit_scriptable);
    //Initialize the python instance
    PyStatus status = init_python("test");
    

    Py_Initialize();
    
    //Run a simple string
    //PyRun_SimpleString("from time import time,ctime\n"
    //                  "print('Today is',ctime(time()))\n");

    std::cout << "[C++] Executing engine_user.py\n";
    FILE* PScriptFile = fopen("engine_user.py", "r");
    if(PScriptFile) {
        PyRun_SimpleFile(PScriptFile, "engine_user.py");
        fclose(PScriptFile);
    }
   
    //Close the python instance
    Py_Finalize();

    std::cout << "[C++] Exiting normally.\n";
    return 0;
}
