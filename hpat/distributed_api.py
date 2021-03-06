from numba import types
from numba.typing.templates import infer_global, AbstractTemplate, infer
from numba.typing import signature
from numba.extending import models, register_model
import time

from enum import Enum

# get size dynamically from C code (mpich 3.2 is 4 bytes but openmpi 1.6 is 8)
import hdist
mpi_req_numba_type = getattr(types, "int"+str(8 * hdist.mpi_req_num_bytes))

class Reduce_Type(Enum):
    Sum = 0
    Prod = 1
    Min = 2
    Max = 3
    Argmin = 4
    Argmax = 5


def get_rank():  # pragma: no cover
    """dummy function for C mpi get_rank"""
    return 0


def barrier():  # pragma: no cover
    return 0


def get_size():  # pragma: no cover
    """dummy function for C mpi get_size"""
    return 0


def get_start(total_size, pes, rank):  # pragma: no cover
    """get end point of range for parfor division"""
    return 0


def get_end(total_size, pes, rank):  # pragma: no cover
    """get end point of range for parfor division"""
    return 0


def get_node_portion(total_size, pes, rank):  # pragma: no cover
    """get portion of size for alloc division"""
    return 0


def dist_reduce(value):  # pragma: no cover
    """dummy to implement simple reductions"""
    return value


def dist_arr_reduce(arr):  # pragma: no cover
    """dummy to implement array reductions"""
    return -1


def dist_cumsum(arr):  # pragma: no cover
    """dummy to implement cumsum"""
    return arr


def dist_cumprod(arr):  # pragma: no cover
    """dummy to implement cumprod"""
    return arr


def dist_exscan(value):  # pragma: no cover
    """dummy to implement simple exscan"""
    return value


def dist_setitem(arr, index, val):  # pragma: no cover
    return 0

def allgather(arr, val):  # pragma: no cover
    arr[0] = val

def dist_time():  # pragma: no cover
    return time.time()

def dist_return(A):  # pragma: no cover
    return A

def dist_input(A):  # pragma: no cover
    return A

def threaded_input(A):  # pragma: no cover
    return A

def threaded_return(A):  # pragma: no cover
    return A

def rebalance_array(A):
    return A

def rebalance_array_parallel(A):
    return A

from numba.extending import overload

@overload(rebalance_array)
@overload(dist_return)
@overload(dist_input)
@overload(threaded_input)
@overload(threaded_return)
def dist_return_overload(column):
    return dist_return

def irecv():  # pragma: no cover
    return 0


def isend():  # pragma: no cover
    return 0


def wait():  # pragma: no cover
    return 0

def waitall():  # pragma: no cover
    return 0

@infer_global(allgather)
class DistAllgather(AbstractTemplate):
    def generic(self, args, kws):
        assert not kws
        assert len(args) == 2  # array and val
        return signature(types.none, *args)

@infer_global(rebalance_array_parallel)
class DistRebalanceParallel(AbstractTemplate):
    def generic(self, args, kws):
        assert not kws
        assert len(args) == 2  # array and count
        return signature(args[0], *args)


@infer_global(get_rank)
class DistRank(AbstractTemplate):
    def generic(self, args, kws):
        assert not kws
        assert len(args) == 0
        return signature(types.int32, *args)


@infer_global(get_size)
class DistSize(AbstractTemplate):
    def generic(self, args, kws):
        assert not kws
        assert len(args) == 0
        return signature(types.int32, *args)


@infer_global(get_start)
class DistStart(AbstractTemplate):
    def generic(self, args, kws):
        assert not kws
        assert len(args) == 3
        return signature(types.int64, *args)


@infer_global(get_end)
class DistEnd(AbstractTemplate):
    def generic(self, args, kws):
        assert not kws
        assert len(args) == 3
        return signature(types.int64, *args)


@infer_global(get_node_portion)
class DistPortion(AbstractTemplate):
    def generic(self, args, kws):
        assert not kws
        assert len(args) == 3
        return signature(types.int64, *args)


@infer_global(dist_reduce)
class DistReduce(AbstractTemplate):
    def generic(self, args, kws):
        assert not kws
        assert len(args) == 2  # value and reduce_op
        return signature(args[0], *args)


@infer_global(dist_exscan)
class DistExscan(AbstractTemplate):
    def generic(self, args, kws):
        assert not kws
        assert len(args) == 1
        return signature(args[0], *args)


@infer_global(dist_arr_reduce)
class DistArrReduce(AbstractTemplate):
    def generic(self, args, kws):
        assert not kws
        assert len(args) == 2  # value and reduce_op
        return signature(types.int32, *args)


@infer_global(time.time)
class DistTime(AbstractTemplate):
    def generic(self, args, kws):
        assert not kws
        assert len(args) == 0
        return signature(types.float64, *args)


@infer_global(dist_time)
class DistDistTime(AbstractTemplate):
    def generic(self, args, kws):
        assert not kws
        assert len(args) == 0
        return signature(types.float64, *args)


@infer_global(barrier)
class DistBarrier(AbstractTemplate):
    def generic(self, args, kws):
        assert not kws
        assert len(args) == 0
        return signature(types.int32, *args)


@infer_global(dist_cumsum)
@infer_global(dist_cumprod)
class DistCumsumprod(AbstractTemplate):
    def generic(self, args, kws):
        assert not kws
        assert len(args) == 2
        return signature(types.int32, *args)


@infer_global(irecv)
@infer_global(isend)
class DistIRecv(AbstractTemplate):
    def generic(self, args, kws):
        assert not kws
        assert len(args) in [4, 5]
        return signature(mpi_req_numba_type, *args)


@infer_global(wait)
class DistWait(AbstractTemplate):
    def generic(self, args, kws):
        assert not kws
        assert len(args) == 2
        return signature(types.int32, *args)

@infer_global(waitall)
class DistWait(AbstractTemplate):
    def generic(self, args, kws):
        assert not kws
        assert len(args) == 2 and args == (types.int32, req_array_type)
        return signature(types.none, *args)

# @infer_global(dist_setitem)
# class DistSetitem(AbstractTemplate):
#     def generic(self, args, kws):
#         assert not kws
#         assert len(args)==5
#         return signature(types.int32, *args)


class ReqArrayType(types.Type):
    def __init__(self):
        super(ReqArrayType, self).__init__(
            name='ReqArrayType()')

req_array_type = ReqArrayType()
register_model(ReqArrayType)(models.OpaqueModel)

def comm_req_alloc():
    return 0

def comm_req_dealloc():
    return 0

@infer_global(comm_req_alloc)
class DistCommReqAlloc(AbstractTemplate):
    def generic(self, args, kws):
        assert not kws
        assert len(args) == 1 and args[0] == types.int32
        return signature(req_array_type, *args)

@infer_global(comm_req_dealloc)
class DistCommReqDeAlloc(AbstractTemplate):
    def generic(self, args, kws):
        assert not kws
        assert len(args) == 1 and args[0] == req_array_type
        return signature(types.none, *args)

@infer
class SetItemReqArray(AbstractTemplate):
    key = "setitem"

    def generic(self, args, kws):
        assert not kws
        [ary, idx, val] = args
        if isinstance(ary, ReqArrayType) and idx == types.intp and val == mpi_req_numba_type:
            return signature(types.none, *args)
