
import triton
import triton.language as tl
# from torch._inductor.ir import ReductionHint
# from torch._inductor.ir import TileHint
# from intel_extension_for_pytorch._inductor.xpu.triton_heuristics import AutotuneHint, persistent_reduction
# from torch._inductor.utils import instance_descriptor
import triton_helpers

from helper import rand_strided
import torch
# from intel_extension_for_pytorch._C import _getCurrentRawStream as get_xpu_stream
# from torch._inductor.triton_heuristics import grid

# @persistent_reduction(
#     size_hints=[262144, 1024],
#     reduction_hint=ReductionHint.INNER,
#     filename=__file__,
#     meta={'signature': {0: '*bf16', 1: '*bf16', 2: 'i32', 3: 'i32'}, 'device': 0, 'device_type': 'xpu', 'constants': {}, 'mutated_arg_names': [], 'autotune_hints': set(), 'kernel_name': 'triton_per_fused__softmax_10', 'configs': [instance_descriptor(divisible_by_16=(0, 1, 2), equal_to_1=(), ids_of_folded_args=(), divisible_by_8=(2,))]}
# )
@triton.jit
def triton_per_fused__softmax_10(in_ptr0, out_ptr2, xnumel, rnumel):
    xnumel = 246272
    XBLOCK: tl.constexpr = 1
    rnumel = 962
    RBLOCK: tl.constexpr = 1024
    xoffset = tl.program_id(0) * XBLOCK
    xindex = tl.full([1], xoffset, tl.int32)
    xmask = xindex < xnumel
    rindex = tl.arange(0, RBLOCK)[:]
    rmask = rindex < rnumel
    r1 = rindex
    x0 = xindex
    tmp0 = tl.load(in_ptr0 + (r1 + (962*x0)), rmask & xmask, other=0).to(tl.float32)
    tmp1 = tmp0.to(tl.float32)
    tmp2 = tl.broadcast_to(tmp1, [RBLOCK])
    tmp4 = tl.where(rmask & xmask, tmp2, float("-inf"))
    tmp5 = triton_helpers.promote_to_tensor(triton_helpers.max2(tmp4, 0))
    tmp6 = tmp1 - tmp5
    tmp7 = tl.exp(tmp6)
    tmp8 = tl.broadcast_to(tmp7, [RBLOCK])
    tmp10 = tl.where(rmask & xmask, tmp8, 0)
    tmp11 = triton_helpers.promote_to_tensor(tl.sum(tmp10, 0))
    tmp12 = tmp7 / tmp11
    tmp13 = tmp12.to(tl.float32)
    tl.store(out_ptr2 + (r1 + (962*x0)), tmp13, rmask & xmask)


def get_args():
    arg_0 = rand_strided((256, 962, 962), (925444, 962, 1), device='xpu:0', dtype=torch.bfloat16)
    arg_1 = rand_strided((64, 4, 962, 962), (3701776, 925444, 962, 1), device='xpu:0', dtype=torch.bfloat16)
    return arg_0, arg_1,


def call(args):
    # with torch.xpu._DeviceGuard(0):
    #     torch.xpu.set_device(0)
    #     stream0 = get_xpu_stream(0)
    grid=lambda meta: (246272, )
    triton_per_fused__softmax_10[grid](*args, 246272, 962)


# def benchmark_all_configs(args):
#     with torch.xpu._DeviceGuard(0):
#         torch.xpu.set_device(0)
#         return triton_per_fused__softmax_10.benchmark_all_configs(*args, 246272, 962, grid=grid(246272))


if __name__ == '__main__':
    # from torch._inductor.utils import get_num_bytes
    # from intel_extension_for_pytorch._inductor.xpu.utils import do_bench

    args = get_args()
    call(args)
    # ms = do_bench(lambda: call(args), rep=40, fast_flush=True)
    # num_gb = get_num_bytes(*args, num_in_out_args=0) / 1e9
    # gb_per_s = num_gb / (ms / 1e3)
    # print(f"{ms:.3f}ms    {num_gb:.3f}GB    {gb_per_s:.2f}GB/s")