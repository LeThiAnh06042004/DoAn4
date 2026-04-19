import allure


def execute_steps(dispatcher, steps, logger):
    skip_block = False

    logger.info("START TEST EXECUTION")

    for i, step in enumerate(steps, 1):
        keyword = step["keyword"]
        locator = step.get("locator", "")
        value = step.get("value", "")

        step_name = f"STEP {i}: {keyword} | {locator} | {value}"
        logger.info(step_name)

        # ===== ALLURE STEP =====
        with allure.step(step_name):

            # ===== IF =====
            if keyword == "IF":
                condition_keyword, condition_locator = value.split(":")
                result = dispatcher.execute(condition_keyword, [condition_locator])
                skip_block = not result
                continue

            # ===== ELSE =====
            if keyword == "ELSE":
                skip_block = not skip_block
                continue

            # ===== END_IF =====
            if keyword == "END_IF":
                skip_block = False
                continue

            # ===== SKIP =====
            if skip_block:
                logger.info("SKIPPED")
                continue

            # ===== NORMAL STEP =====
            args = []
            if locator:
                args.append(locator)
            if value:
                args.append(value)

            try:
                result = dispatcher.execute(keyword, args)

                # VERIFY fail
                if keyword.startswith("VERIFY") and result is False:
                    raise Exception(f"{keyword} FAILED")

                logger.info("PASS")

            except Exception as e:
                logger.error(f"FAIL: {e}")
                raise