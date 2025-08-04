from cli import parse_args
from core.evaluator import CoverageEvaluator
from core.runner import CoverageRunner
from core.modes import CoverageMode
from core.config import CovalyzerConfig

def eval(config: CovalyzerConfig):
    evaluator = CoverageEvaluator(
            profraw_dir = config.output_dir,
            coverage_binary = config.coverage_binary,
            output_dir = config.output_dir
            )
    evaluator.evaluate()

    
def main():
    config = parse_args()
    runner = CoverageRunner(config)

    print(f"{config.mode}")

    match config.mode:
        case CoverageMode.ALL_TESTCASES:
            runner.run_all_testcases_stateless(batch_size=1000)
            eval(config=config)
            runner.close()
        case CoverageMode.EVAL_ONLY:
            eval(config=config)
        case CoverageMode.FUZZBENCH_LIKE:
            runner.run_fuzzbench_mode()
            eval(config=config)
            runner.close()
        case _:
            print("Not implemented yet :(")



    #if config.mode.value == CoverageMode.ALL_TESTCASES.value:
    #    runner.run_all_testcases_stateless(batch_size=1000)
    #elif config.mode.value == CoverageMode.EVAL_ONLY.value:
    #    print("Just doing evaluation....")
    #else:
    #    print("Not yet implemented :(")

    #runner.close()
    #evaluator = CoverageEvaluator(
    #    profraw_dir = config.output_dir,
    #    coverage_binary = config.coverage_binary,
    #    output_dir = config.output_dir
    #    )
    #evaluator.evaluate()


if __name__ == "__main__":
    main()


